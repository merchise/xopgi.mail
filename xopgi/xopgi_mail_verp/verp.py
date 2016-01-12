# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.router
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

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


from xoutil import logger as _logger
from xoutil.string import safe_encode

from xoeuf.osv.model_extensions import search_browse

from openerp import SUPERUSER_ID

from openerp.models import Model
from openerp.osv import fields

from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData
from openerp.addons.mail.mail_thread import decode_header
from openerp.addons.mail.mail_message import decode

from .mail_bounce_model import BOUNCE_MODEL


def valid_email(name, email):
    try:
        return '@' in email
    except:
        return False


def get_recipients(message, include_cc=False):
    'Return the list of (name, email) of the message recipients.'
    # TODO: use openerp.tools.email_split(text)
    from email.utils import getaddresses
    raw_recipients = [decode_header(message, 'To')]
    if include_cc:
        raw_recipients.append(decode_header(message, 'Cc'))
    recipients = [
        addr for addr in getaddresses(raw_recipients)
        if valid_email(*addr)
    ]
    return recipients


class BounceRecord(Model):
    '''An index for bounce address to message, thread and recipient.

    This model encodes the same information of old VERP addresses but allow a
    simpler address, like: ``bounces+nchH787dnccb@example.com``.

    '''
    _name = 'xopgi.verp.record'

    _columns = dict(
        bounce_alias=fields.char(
            help=('The alias where the bounce was sent to. You may change the'
                  'alias configuration midways and this will still work'),
            required=True,
            default='bounces'
        ),
        thread_index=fields.char(
            help='The unique index reference for the thread.',
            required=True,
            index=True,
        ),
        message_id=fields.many2one(
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
        ),
        reference=fields.char(
            help='The unique part for the bounce address.',
            size=100,
            required=True,
            index=True,
        ),
        recipient=fields.char(
            help='The recipient for which this VERP address was created',
            required=True,
            index=True,
        ),
    )

    _sql_constraints = [
        ('verp_unique', 'unique (reference)', 'The VERP is duplicated.'),
    ]

    def create(self, cr, uid, vals, context=None):
        from openerp.addons.mail.xopgi.index import generate_reference
        reference = generate_reference(
            lambda r: self.search(cr, uid, [('reference', '=', r)]),
            start=3,
            lower=True
        )
        assert reference
        vals.update(reference=reference)
        res = super(BounceRecord, self).create(cr, uid, vals, context=context)
        if res:
            # I don't care about the id
            return reference

    def cleanup(self, cr, uid, context=None):
        '''Remove all bounce address references that are too old.

        This should be called in a cron task.

        '''
        cr.execute('''
           WITH aged AS (
              SELECT id, ((NOW() at time zone 'UTC') - create_date) AS age
              FROM xopgi_verp_record
           ) SELECT id FROM aged WHERE age >= %s
        ''', ('10 days', ))
        elders = [row[0] for row in cr.fetchall()]
        if elders:
            self.unlink(cr, SUPERUSER_ID, elders, context=context)


class BouncedMailRouter(MailRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        route = cls._message_route_check_bounce(obj, cr, uid, message)
        if route and cls._is_auto_responded(obj, cr, uid, message):
            # If the message is an auto-responded (e.g Out of Office) message
            # it will be also delivered to the bounce VERP address, but we
            # should not treat it as bounce and let it be placed according to
            # In-Reply-To.
            return False
        else:
            from flufl.bounce import scan_message
            # Some fucked MTAs send bounce messages to the From address
            # instead of the Return Path.  Let's pretend all delivery-status
            # are bounces or if the scan_message finds any failed address...
            #
            # We can't find the right thread though.
            content_type = message.get('Content-Type', '')
            delivery_status = (content_type.startswith('message/report') and
                               'report-type=delivery-status' in content_type)
            bounce = delivery_status or bool(scan_message(message))
            if bounce:
                _logger.warn('Silly MTA found',
                             extra=dict(message=message.items()))
            return bounce, None

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        bounce = data
        if bounce:
            route = cls._get_route(obj, cr, uid, bounce)
            # We assume a bounce should never create anything else.  What's
            # the point for creating a lead, or task from a
            # bounce... Specially if the alias is bound to some ids.  This
            # only could happen if another router is in place and that would
            # be a design error.
            routes[:] = [route]
        else:
            # Means no route, ie. a bounce but invalid: should not create
            # anything.
            routes[:] = []
        return routes

    @classmethod
    def _is_auto_responded(cls, obj, cr, uid, message):
        '''Check if the message seems to be an auto-responded message and not
        actually a bounce.

        You should review the RFC 3834, for better understanding this method.

        .. warning:: You should only call this method if the `message` is sent
           to VERP address.

        In the sense of this method "Auto responded" messages include:

        - Any sort of message that is sent automatically in reply to a
          message.  Example is a "vacation" notification.  RFC 3834.

        - Any sort of message indicating the disposition of another message.
          Example is a notification of a message being read by any of its
          recipients.  RFC 3798.

        '''
        replied = 'In-Reply-To' in message
        how = message.get('Auto-Submitted', '')
        if how.startswith('auto-replied'):
            # Bounces SHOULD NOT have an In-Reply-To, but SHOULD have an
            # Auto-Submitted.
            return replied
        elif message['X-Autoreply'] == 'yes':
            # Some MTAs also include this, but I will refuse them unless an
            # In-Reply-To is provided.
            return replied
        content_type = message.get('Content-Type', '')
        if content_type.startswith('message/report'):
            # Disposition notifications should not be considered bounces.
            # However they SHOULD be delivered to the Return-Path, so we need
            # to deal with them.  They are not (strictly speaking) auto
            # responded replies in the sense of RFC 3834, but since we're
            # trying to actually determine if this is a bounce, let's not
            # considered cases are assumed to be bounces.
            return 'report-type=disposition-notification' in content_type
        return False

    @classmethod
    def _void_return_path(cls, return_path):
        'Indicates if this a bouncy Return-Path.'
        from .common import VOID_EMAIL_ADDRESS
        res = not return_path or return_path == VOID_EMAIL_ADDRESS
        if not res:
            # Some MTAs place "<MAILER-DAEMON>" return path upon delivery.
            res = not valid_email(return_path[1:-1])
        return res

    @classmethod
    def is_bouncelike(self, obj, cr, uid, rcpt, context=None):
        from .common import get_bounce_alias
        bounce_alias = get_bounce_alias(obj.pool, cr, uid, context=context)
        if not bounce_alias:
            return False
        localpart, _ = rcpt.rsplit('@', 1)
        if '+' in localpart:
            alias, reference = localpart.split('+', 1)
            return alias == bounce_alias
        return False

    @classmethod
    def _message_route_check_bounce(self, obj, cr, uid, message):
        """Verify that the email_to is the bounce alias.

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
                found = search_browse(
                    obj.pool['xopgi.verp.record'],
                    cr, uid,
                    [('bounce_alias', '=', alias),
                     ('reference', '=', reference)],
                    limit=1,
                    ensure_list=False
                )
                if found:
                    Threads = obj.pool['mail.thread']
                    model, thread_id = Threads._threadref_by_index(
                        cr, SUPERUSER_ID, found.thread_index
                    )
                    if model and thread_id:
                        return (found.message_id, model, thread_id,
                                found.recipient)
        # Not a known bounce
        return None

    @classmethod
    def _get_route(self, obj, cr, uid, bouncedata):
        return (BOUNCE_MODEL, bouncedata, {}, uid, None)


class VariableEnvReturnPathTransport(MailTransportRouter):
    '''A Variable Envelop Return Path Transport.

    Along with the router takes care of matching outgoing messages with
    bounces.

    '''
    @classmethod
    def _get_bounce_address(cls, obj, cr, uid, message, mail, email_to,
                            context=None):
        '''Compute the bounce address.

        '''
        from .common import VOID_EMAIL_ADDRESS
        if mail.email_from == VOID_EMAIL_ADDRESS:
            # This is a bounce notification, so don't we should not generate a
            # VERP address.
            return None
        if not mail.mail_message_id:
            # I can't provide a VERP bounce address without a message id.
            return None
        assert mail.mail_message_id.id == message.id
        from .common import get_bounce_alias
        bounce_alias = get_bounce_alias(obj.pool, cr, uid, context=context)
        if not bounce_alias:
            return None
        get_param = obj.pool['ir.config_parameter'].get_param
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if not domain or not message.thread_index:
            return None
        Records = obj.pool['xopgi.verp.record']
        reference = Records.create(
            cr, uid,
            dict(
                bounce_alias=bounce_alias,
                message_id=message.id,
                thread_index=message.thread_index,
                recipient=decode(
                    # decode assumes str, but mail.email_to may yield unicode
                    safe_encode(mail.email_to or email_to)
                )
            ),
            context=context)
        return '%s+%s@%s' % (bounce_alias, reference, domain)

    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        '''Test whether the `message` should be delivered with VERP.

        Return ``(True, {'address': address})`` if test succeeds, otherwise
        return ``(False, None)``.

        The address in a positive result is the VERP address generated for the
        message.

        If the message contains the 'Auto-Submitted' header, no VERP will be
        performed.  The rationale for this, is that automatic responders won't
        get any useful information from a bounce.

        '''
        context = context if context else {}
        mail_id = context.get('mail_id', False) if context else False
        if not mail_id:
            return False, None
        automatic = message['Auto-Submitted']
        if automatic:
            return False, None
        msg, _ = self.get_message_objects(obj, cr, uid, message,
                                          context=context)
        if msg:
            msg = msg[0] if isinstance(msg, list) else msg
            mail = obj.pool['mail.mail'].browse(cr, uid, mail_id,
                                                context=context)
            address = self._get_bounce_address(obj, cr, uid, msg, mail,
                                               mail.email_to
                                               or message['To'],
                                               context=context)
            return bool(address), dict(address=address)
        return False, None

    def prepare_message(self, obj, cr, uid, message, data=None, context=None):
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
