#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A MailRouter for bounced messages.


For each outgoing message we create unique bounce address (VERP_) of the
form::

   <alias>+<unique bounce reference>

The `unique bounce reference` is a pseudo-random chain of chars and digits
that is kept in a index and maps to:

- The message being sent
- The thread the message belongs to.
- The recipient to which this bounce reference was generated.

  .. note:: A single message may be sent to several recipients.  However, we
     generate an email per recipient.

.. warning:: Bounces should never fail.

   When processing a bounce message, we SHOULD NEVER fail.  This could be done
   at the MTA level, since a bounce should not contain a MAIL FROM.

As noted in SRS_ does not scale.  But neither does Odoo.


.. _VERP: https://en.wikipedia.org/wiki/Variable_envelope_return_path
.. _SRS: https://en.wikipedia.org/wiki/Sender_Rewriting_Scheme

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.future.codecs import safe_encode

from xoeuf import api, models, fields
from xoeuf.odoo.addons.xopgi_mail_threads import (
    MailTransportRouter,
    TransportRouteData
)
from xoeuf.odoo.addons.xopgi_mail_threads.utils import (
    decode_smtp_header as decode_header,
    create_ignore_route,
    is_automatic_response,
    get_automatic_response_type,
    DELIVERY_STATUS_NOTIFICATION,
)

from ..common import (
    VOID_EMAIL_ADDRESS,
    get_bounce_alias,
    get_recipients,
)

from ..mail_bounce_model import (
    BounceVirtualId,
    BOUNCE_MODEL,
    AUTOMATIC_RESPONSE_MODEL
)


class BounceRecord(models.Model):
    '''An index for bounce address to message, thread and recipient.

    This model encodes the same information of old VERP addresses but allow a
    simpler address, like: ``bounces+nchH787dnccb@example.com``.

    '''
    _name = 'xopgi.verp.record'

    bounce_alias = fields.Char(
        help=('The alias where the bounce was sent to. You may change the'
              'alias configuration midways and this will still work'),
        required=True,
        default='bounces'
    )

    thread_index = fields.Char(
        help='The unique index reference for the thread.',
        required=True,
        index=True,
    )

    message_id = fields.Many2one(
        'mail.message',
        required=True,
        # ondelete=cascade: If the message is delete remove the VERP
        # address.  This happens for invitations, for instance.  The
        # message is create and the bounce address is properly generated,
        # but afterwards the message is removed.  This make the bounce
        # reference ephemeral for these cases, but if the message is lost
        # we won't be able to know who to notify.
        ondelete="cascade",
        help=('The message id originating this notification. This allows '
              'to know who to notify about bounces.')
    )
    reference = fields.Char(
        help='The unique part for the bounce address.',
        size=100,
        required=True,
        index=True,
    )

    recipient = fields.Char(
        help='The recipient for which this VERP address was created',
        required=True,
        index=True,
    )

    _sql_constraints = [
        ('verp_unique', 'unique (reference)', 'The VERP is duplicated.'),
    ]

    @api.model
    @api.returns('self', lambda r: r.reference)  # return the reference
    def create(self, vals):
        try:
            from openerp.addons.mail.xopgi.index import generate_reference
        except ImportError:
            try:  # Odoo 9
                from openerp.addons.mail.models.xopgi.index import generate_reference
            except ImportError:  # Odoo 10
                from odoo.addons.mail.models.xopgi.index import generate_reference
        reference = generate_reference(
            lambda r: self.search([('reference', '=', r)]),
            start=3,
            lower=True
        )
        assert reference
        vals.update(reference=reference)
        return super(BounceRecord, self).create(vals)

    @api.model
    def cleanup(self):
        '''Remove all bounce address references that are too old.

        This should be called in a cron task.

        '''
        self._cr.execute('''
           WITH aged AS (
              SELECT id, ((NOW() at time zone 'UTC') - create_date) AS age
              FROM xopgi_verp_record
           ) SELECT id FROM aged WHERE age >= %s
        ''', ('10 days', ))
        elders = [row[0] for row in self._cr.fetchall()]
        if elders:
            self.sudo().browse(elders).unlink()


class BouncedMailRouter(object):
    # Note that even though this class follows the MailRouter it MUST NOT
    # inherit from MailRouter, so that this router is properly coordinated.
    @classmethod
    def query(cls, obj, message):
        route = cls._message_route_check_bounce(obj, message)
        if route:
            # If the message is an auto-responded (e.g Out of Office) message
            # it will be also delivered to the bounce VERP address.
            # Some mailers send auto-responses to the Return-Path address
            # correctly but fail to include the Auto-Submitted header.
            # However is too hard to find out if this is the case...
            return True, route
        return False, None

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        bounce = data
        if bounce:
            if isinstance(bounce, BounceVirtualId):
                resp_type = get_automatic_response_type(bounce.message)
                if resp_type and resp_type != DELIVERY_STATUS_NOTIFICATION:
                    route = cls._get_automatic_response_route(obj, bounce)
                else:
                    route = cls._get_bounce_route(obj, bounce)
                # We assume a bounce should never create anything else.  What's
                # the point for creating a lead, or task from abounce...
                # Specially if the alias is bound to some ids.  This only
                # could happen if another router is in place and that would
                # be a design error.
                routes[:] = [route]
            else:
                routes[:] = [create_ignore_route(message)]
        else:
            # Means no route, ie. a bounce but invalid: should not create
            # anything.
            routes[:] = []
        return routes

    @classmethod
    def is_bouncelike(self, obj, rcpt):
        bounce_alias = get_bounce_alias(obj)
        if not bounce_alias:
            return False
        localpart, _ = rcpt.rsplit('@', 1)
        if '+' in localpart:
            alias, reference = localpart.split('+', 1)
            return alias == bounce_alias
        return False

    @classmethod
    def _message_route_check_bounce(self, obj, message):
        # type: (Any, email.Message) -> Union[bool, BounceVirtualId]
        """Verify that the email_to is the bounce alias.

        Return False if the message is not being sent to a possible VERP
        bounce address.

        Return a BounceVirtualId if the message is being sent to known VERP
        bounce address.

        Return True if the message is being sent to a *possible* VERP bounce
        address but we might have forgot its record already.

        Notice this method will return any route matching a bounce address.
        You should deal with forgery elsewhere.

        """
        recipients = get_recipients(message)
        found = None
        while not found and recipients:
            _name, recipient = recipients.pop(0)
            localpart, _ = recipient.rsplit('@', 1)
            if '+' in localpart:
                alias, reference = localpart.split('+', 1)
                found = obj.env['xopgi.verp.record'].search(
                    [('bounce_alias', '=', alias),
                     ('reference', '=', reference)],
                    limit=1,
                )
                if found:
                    Threads = obj.env['mail.thread']
                    model, thread_id = Threads.sudo()._threadref_by_index(
                        found.thread_index
                    )
                    if model and thread_id:
                        return BounceVirtualId(
                            found.message_id, model, thread_id,
                            found.recipient, message
                        )
                    else:
                        return True
                elif alias == get_bounce_alias(obj):
                    return True
        # Not a known bounce
        return False

    @classmethod
    def _get_bounce_route(self, obj, bouncedata):
        return (BOUNCE_MODEL, bouncedata, {}, obj._uid, None)

    @classmethod
    def _get_automatic_response_route(self, obj, bouncedata):
        return (AUTOMATIC_RESPONSE_MODEL, bouncedata, {}, obj._uid, None)


class VariableEnvReturnPathTransport(MailTransportRouter):
    '''A Variable Envelop Return Path Transport.

    Along with the router takes care of matching outgoing messages with
    bounces.

    '''
    @classmethod
    def _get_bounce_address(cls, obj, message, mail, email_to):
        '''Compute the bounce address.

        '''
        if mail.email_from == VOID_EMAIL_ADDRESS:
            # This is a bounce notification, so don't we should not generate a
            # VERP address.
            return None
        if not mail.mail_message_id:
            # I can't provide a VERP bounce address without a message id.
            return None
        assert mail.mail_message_id.id == message.id
        bounce_alias = get_bounce_alias(obj)
        if not bounce_alias:
            return None
        get_param = obj.env['ir.config_parameter'].get_param
        domain = get_param('mail.catchall.domain')
        if not domain or not message.thread_index:
            return None
        Records = obj.env['xopgi.verp.record']
        record = Records.create(dict(
            bounce_alias=bounce_alias,
            message_id=message.id,
            thread_index=message.thread_index,
            recipient=decode_header(
                # decode assumes str, but mail.email_to may yield unicode
                safe_encode(mail.email_to or email_to)
            )
        ))
        return '%s+%s@%s' % (bounce_alias, record.reference, domain)

    @classmethod
    def query(self, obj, message):
        '''Test whether the `message` should be delivered with VERP.

        Return ``(True, {'address': address})`` if test succeeds, otherwise
        return ``(False, None)``.

        The address in a positive result is the VERP address generated for the
        message.

        If the message is an automatic response (RFCs 3834, 3464 and 3798), no
        VERP will be performed.  The rationale for this, is that Return-Path
        and Reply-To headers in automatic responses MUST be treated different
        for avoiding loops.

        '''
        context = obj._context
        mail_id = context.get('verp_mail_id', False) if context else False
        if not mail_id:
            return False, None
        automatic = is_automatic_response(message)
        if automatic:
            # Outgoing Auto-Submitted should not be marked with our VERP
            # addresses.
            return False, None
        msg, _ = self.get_message_objects(obj, message)
        if msg:
            msg = msg[0]
            mail = obj.env['mail.mail'].browse(mail_id)
            address = self._get_bounce_address(
                obj, msg, mail,
                mail.email_to or message['To']
            )
            return bool(address), dict(address=address)
        return False, None

    def prepare_message(self, obj, message, data=None):
        '''Add the bounce address to the message.

        '''
        address = data['address']
        del message['Return-Path']  # Ensure a single Return-Path
        message['Return-Path'] = address
        if message['Disposition-Notification-To']:
            # Any disposition request will be invalid after the Return-Path is
            # changed.  See RFC 3798 section 2.1.
            del message['Disposition-Notification-To']
            message = address
        return TransportRouteData(message, {})
