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
                        absolute_import as _py3_abs_import)

from xoutil import logger as _logger

from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData
from openerp.addons.xopgi_mail_threads.utils import set_message_from
from openerp.addons.xopgi_mail_threads.utils import set_message_sender


#
# This pair of Router & Transport avoid the mail-sending cycles when two
# or more parties in a single thread have auto-responders:
#
# 1- Party A sends a message
# 2- Odoo resends to Party B
# 3- The party B's auto-responders send the automatic message to Odoo
# 4- Odoo resends to Party A
# 5- The Party A's auto-responders send the automatic message to Odoo.
#
# This, of course, assumes that both Party A and B have buggy auto-responders
# that auto-respond to messages which are themselves auto-submitted.
#
# The VERP Transport already bails out when the message being sent is an
# auto-submitted one.  So this addon plays well with VERP.
#
# What we do is that when sending auto-submitted messages we replace the
# Return-Path, Reply-To, Sender and From with a 'breaking-cycle' address, if a
# auto-submitted message is received for any 'breaking-cycle' address is
# simply ignored.
#


# The default alias for breaking cycle address.  You may configure the
# parameter 'mail.breaking-cycle.alias'.
DEFAULT_BREAKING_PREFIX = 'breaking-cycle'
BREAKING_ALIAS_PARAMETER = 'mail.breaking-cycle.alias'


class BreakingCyclesTransport(MailTransportRouter):
    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        msg, _ = self.get_message_objects(obj, cr, uid, message,
                                          context=context)
        if message['Auto-Submitted']:
            address = self._get_breaking_address(
                obj, cr, uid, msg.thread_index, context=context)
            _logger.info('Re-sending auto-submitted message with a '
                         'breaking-cycle address %s', address)
            return bool(address), address
        return False, None

    def prepare_message(self, obj, cr, uid, message, address=None,
                        context=None):
        assert address
        self._set_headers(obj, cr, uid, message, address,
                          context=context)
        return TransportRouteData(message, {})

    @classmethod
    def _set_headers(cls, obj, cr, uid, message, address,
                     context=None):
        del message['Reply-To']
        message['Reply-To'] = address
        del message['Return-Path']
        message['Return-Path'] = address
        set_message_sender(message, address)
        set_message_from(message, address, address_only=True)

    @classmethod
    def _get_breaking_address(cls, obj, cr, uid, thread_index, context=None):
        get_param = obj.pool['ir.config_parameter'].get_param
        alias = get_param(cr, uid, BREAKING_ALIAS_PARAMETER,
                          default=DEFAULT_BREAKING_PREFIX, context=context)
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if domain:
            return '%s+%s@%s' % (alias, thread_index, domain)
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
        if message['Auto-Submitted']:
            # If the message we're receiving is not an auto-submitted one,
            # it's not a cycle.  This would be the case of:
            #
            # 1. Party A sends an auto-submitted message
            # 2. Odoo resends that message to Party B.
            # 3. Party B does not auto-respond, and that's just fine.
            # 4. Later Party B replies but uses the address in the
            #    auto-submitted message to do it.
            #
            # In this, although the address would be a breaking cycle is not
            # actually a cycle.
            #
            # The only problem with this is there's a auto-responder that does
            # not use the Auto-Submitted header.  As we've seen some use the
            # From address as the recipient for the auto-submitted message and
            # that's not what the RFC recommends.  However, the previous
            # depiction is likely to happen is we ever allow an auto-submitted
            # message to go out (as we do).
            #
            recipients = [
                email for _, email in getaddresses(headers)
                if cls._is_breaking_cycle_address(cls, obj, cr, uid, email)
            ]
            # If any recipient is a breaking cycle address, break it!
            return bool(recipients)
        else:
            return False

    @classmethod
    def _is_breaking_cycle_address(cls, obj, cr, uid, address, context=None):
        get_param = obj.pool['ir.config_parameter'].get_param
        prefix = get_param(cr, uid, BREAKING_ALIAS_PARAMETER,
                           default=DEFAULT_BREAKING_PREFIX, context=context)
        return address.startswith(prefix + '+')

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        # This method is only called when the router match the breaking-cycles
        # alias.  This means we detected a cycle, and NOTHING should be done
        # with this message.
        routes[:] = []
        return routes
