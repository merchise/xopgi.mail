# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# # xopgi.xopgi_mail_breaking_cycles
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-08



from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from openerp import SUPERUSER_ID
from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData
from openerp.addons.xopgi_mail_threads.utils import set_message_from
from openerp.addons.xopgi_mail_threads.utils import set_message_sender


DEFAULT_REPLYTO_PREFIX = 'catchall'

class BreakingCyclesTransport(MailTransportRouter):
    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        msg, _ = self.get_message_objects(obj, cr, uid, message,
                                         context=context)
        address = self._get_replyto(obj, cr, uid, msg.thread_index,
                                               context=context)
        if message['Auto-Submitted']:
            address = 'breaking-cycles+8jfh764@lahavane.com'
            return bool(address), dict(thread_index=msg.thread_index,
                                       replyto_address=address)
        if msg and msg.thread_index:
            return bool(address), dict(thread_index=msg.thread_index,
                                       replyto_address=address)
        return False, None

    def prepare_message(self, obj, cr, uid, message, data=None, context=None):
        address = data['replyto_address']
        self._set_replyto(obj, cr, uid, message, address,
                                  context=context)
        del message['Return-Path']
        message['Return-Path'] = address
        return TransportRouteData(message, {})

    @classmethod
    def _set_replyto(cls, obj, cr, uid, message, address,
                             context=None):
        del message['Reply-To']
        message['Reply-To'] = address
        set_message_sender(message, address)
        set_message_from(message, address, address_only=True)

    @classmethod
    def _get_replyto(cls, obj, cr, uid, thread_index,
                             context=None):
        get_param = obj.pool['ir.config_parameter'].get_param
        replyto = get_param(cr, uid, 'mail.catchall.alias',
                            default=DEFAULT_REPLYTO_PREFIX,
                            context=context)
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if domain:
            return '%s+%s@%s' % (replyto, thread_index, domain)
        else:
            return None

class BreakingCyclesRouter(MailRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        from email.utils import getaddresses
        from openerp.addons.mail.mail_thread import decode_header
        headers = [
            decode_header(message, 'To'),
            decode_header(message, 'Cc'),
            decode_header(message, 'Delivered-To')
        ]
        recipients = [email for _, email in getaddresses(headers)]
        match = cls._find_replyto(obj, cr, uid, recipients, context=context)
        return match is not None, match

    @classmethod
    def _find_replyto(cls, obj, cr, uid, recipients, context=None):
        from xoutil.string import cut_prefix, cut_suffix
        get_param = obj.pool['ir.config_parameter'].get_param
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if not domain:
            return None
        replyto = get_param(cr, uid, 'mail.replyto.alias',
                            default=DEFAULT_REPLYTO_PREFIX, context=context)
        prefix, suffix = replyto + '+', '@' + domain
        found, model, thread_id = None, None, None
        Threads = obj.pool['mail.thread']
        while not found and recipients:
            res = recipients.pop(0)
            if prefix.startswith('breaking-cycles'):
                model, thread_id = None, None
            elif res.startswith(prefix):
                thread_index = cut_prefix(cut_suffix(res, suffix), prefix)
                model, thread_id = Threads._threadref_by_index(cr, uid,
                                                               thread_index)
                found = bool(model and thread_id)
        return (res, model, thread_id) if found else None

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        def valid(route):
            # A valid route is one that does not shadow our Reply-to and does
            # not create a new thread (the classical fallback to crm.lead)
            return route[0] != model and bool(route[1])
        _, model, thread_id = data
        # Must change the current `routes` **in-place**.
        routes[:] = [route for _pos, route in cls.find_route(routes, valid)]
        # TODO: Find the true user_id
        routes.append((model, thread_id, {}, SUPERUSER_ID, None))
        return routes