#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# disclose
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-06-17

'''Implements a kind of disclosure policy for emails.

Within the footer of an outgoing email, users with a full_email disclosure
will be include, so that others are notified.

.. note:: To protect this implementation from abuse, only 20 users are
   disclosed.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
    from odoo import api, models
    from odoo import tools
    from odoo.addons.base.ir.ir_mail_server import encode_rfc2822_address_header
except ImportError:
    from openerp import tools, SUPERUSER_ID
    from openerp import api, models
    from openerp.release import version_info as ODOO_VERSION_INFO
    from openerp.addons.base.ir.ir_mail_server import encode_rfc2822_address_header

try:
    from odoo.addons.xopgi_mail_threads.transports import (
        MailTransportRouter,
        TransportRouteData
    )
except ImportError:
    from openerp.addons.xopgi_mail_threads.transports import (
        MailTransportRouter,
        TransportRouteData
    )


class ForcedStopIteration(StopIteration):
    '''A StopIteration that means more items were left in the iterable.

    '''
    pass


def first(iterable, many=40):
    '''Return the first `many` items of an iterable.

    This return a generator that stops with a normal StopIteration if all
    items of `iterable` were consumed, and ForcedStopIteration if items were
    left behind.

    .. warning:: When `iterable` has more items that requested, at least,
       another item will be consumed (but not returned) from it.

    '''
    count, iterable = 0, iter(iterable)
    while count < many:
        yield next(iterable)  # StopIteration may be raised here
        count += 1
    try:
        next(iterable)  # Do we have more items?
    except StopIteration:
        raise
    else:
        raise ForcedStopIteration


def joinfirst(iterable, sep, many=40, suffix=''):
    '''Returns the join of the first `many` items in `iterable` using `sep`.

    If there are more items in the iterable that were not included in the
    joined string, the `suffix` is added at the end.
    '''
    class _nonlocal:
        forced = False
        stop = False

    res = first(iterable, many=many)

    def fetchone():
        try:
            return next(res)
        except StopIteration as error:
            _nonlocal.forced = isinstance(error, ForcedStopIteration)
            _nonlocal.stop = True

    chunks = []
    while not _nonlocal.stop:
        item = fetchone()
        if not _nonlocal.stop:
            chunks.append(item)
    return sep.join(chunks) + (suffix if _nonlocal.forced else '')


if ODOO_VERSION_INFO < (9, 0):
    # XXX: For now, we simply replace the entire function in the signature
    class Notification(models.Model):
        _inherit = _name = 'mail.notification'

        @api.model
        def get_signature_footer(self, user_id, res_model=None, res_id=None,
                                 context=None, user_signature=True):
            footer = ""
            if not user_id:
                return footer

            # add user signature
            cr = self.env.cr
            user = self.pool.get("res.users").browse(cr, SUPERUSER_ID, [user_id],
                                                     context=context)[0]
            if user_signature:
                if user.signature:
                    signature = user.signature
                else:
                    signature = "--<br />%s" % user.name
                footer = tools.append_content_to_html(footer, signature,
                                                      plaintext=False)
            if res_model and res_id:
                message = self.pool[res_model].browse(cr, SUPERUSER_ID, res_id)
                partners = (partner.name
                            for partner in message.message_follower_ids
                            if partner and partner.name)
                recipients = joinfirst(partners, sep=', ', suffix=', ...')
                if recipients:
                    footer += '<br/>'
                    disclosed = 'Cc: ' + recipients + '<br/>'
                    footer = tools.append_content_to_html(footer,
                                                          disclosed,
                                                          plaintext=False,
                                                          container_tag='div')
            return footer


class DiscloseRecipientsTransport(MailTransportRouter):
    @classmethod
    def query(cls, obj, message):
        return True, None

    def prepare_message(self, obj, message, data=None):
        from email.utils import COMMASPACE
        msg, _ = self.get_message_objects(obj, message)
        if msg:
            if ODOO_VERSION_INFO < (9, 0):
                # Since Odoo 9, followers are not partners, but a model
                # (channel, follower) that points to the partner.  In Odoo 8,
                # however, the related follower is the partner itself.
                get_partner = lambda partner: partner
            elif (9, 0) <= ODOO_VERSION_INFO < (11, 0):
                get_partner = lambda follower: follower.partner_id
            thread = msg.env[msg.model].browse(msg.res_id)
            reply_to = ''
            partners = (
                encode_rfc2822_address_header('"%s" <%s>' % (partner.name, reply_to))
                for partner in thread.message_follower_ids.mapped(get_partner)
                if partner and partner.name
            )
            message['Cc'] = COMMASPACE.join(partners)
        return TransportRouteData(message, {})
