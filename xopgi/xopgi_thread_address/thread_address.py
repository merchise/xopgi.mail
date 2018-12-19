#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Implement a router/transport that ensures threads have a unique Reply-To
address.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from email.utils import getaddresses

from xoeuf import SUPERUSER_ID
from xoeuf.odoo.addons.xopgi_mail_threads import (
    MailRouter,
    MailTransportRouter,
    TransportRouteData,
)
from xoeuf.odoo.addons.xopgi_mail_threads.utils import (
    decode_header,
    set_message_from,
    set_message_sender,
    set_message_address_header,
)
from xoeuf.odoo.addons.xopgi_mail_threads.stdroutes import BOUNCE_ROUTE_MODEL


import logging
_logger = logging.getLogger(__name__)
del logging


# The default prefix for a Reply-To address.  NOTICE: we suggest to use the
# same as the mail.catchall.alias.  The Reply-To address is constructed as
# ``<replyto alias>+<thread index>@<domain>``.  Notice we use the "+" to
# separate the alias from the thread index, this allows some MTAs to fallback
# to the alias should the entire address fail.
DEFAULT_REPLYTO_PREFIX = 'catchall'


class UniqueAddressTransport(MailTransportRouter):
    @classmethod
    def query(cls, obj, message):
        msg, _ = cls.get_message_objects(obj, message)
        if msg:
            indexes = {m.thread_index for m in msg}
            if len(indexes) > 1:
                _logger.warn(
                    'More than one index retrieved for the same '
                    'message.  Refusing to dispatch the '
                    'message using a unique address and hoping for '
                    'the best.',
                    extra=dict(
                        message_id=message['Message-Id'],
                        indexes=indexes
                    )
                )
                msg = None
            else:
                msg = msg[0]
        if msg and msg.thread_index:
            address = cls._get_replyto_address(obj, msg.thread_index)
            return bool(address), dict(thread_index=msg.thread_index,
                                       replyto_address=address)
        return False, None

    def prepare_message(self, obj, message, data=None):
        thread_index = data['thread_index']
        address = data['replyto_address']
        self._set_replyto_address(obj, message, address)
        # The 'Thread-Index' is just to fuck some Microsoft Offices out there
        # that are not including the References.
        message['X-Odoo-Thread-Index'] = message['Thread-Index'] = thread_index
        return TransportRouteData(message, {})

    @classmethod
    def _set_replyto_address(cls, obj, message, address):
        '''Set the Reply-To address for the message given the thread index.

        Furthermore, all authors and sender are reset so their addresses are
        the same.

        '''
        del message['Reply-To']
        message['Reply-To'] = address
        set_message_address_header(message, 'X-Original-From', message['From'])
        set_message_sender(message, address)
        set_message_from(message, address, address_only=True)

    @classmethod
    def _get_replyto_address(cls, obj, thread_index):
        get_param = obj.env['ir.config_parameter'].get_param
        replymarks = get_param('mail.replyto.alias',
                               default=DEFAULT_REPLYTO_PREFIX)
        # mail.replyto.alias is allowed to contain several aliases separated
        # by commas
        replyto = [alias.strip() for alias in replymarks.split(',')][0]
        domain = get_param('mail.catchall.domain')
        if domain:
            return '%s+%s@%s' % (replyto, thread_index, domain)
        else:
            return None


class UniqueAddressRouter(MailRouter):
    @classmethod
    def query(cls, obj, message):
        headers = [
            decode_header(message, 'To'),
            decode_header(message, 'Cc'),
            decode_header(message, 'Delivered-To')
        ]
        recipients = [email for _, email in getaddresses(headers)]
        match = cls._find_replyto(obj, recipients)
        return match is not None, match

    @classmethod
    def _find_replyto(cls, obj, recipients):
        get_param = obj.env['ir.config_parameter'].get_param
        domain = get_param('mail.catchall.domain')
        if not domain:
            return None
        else:
            domain = '@' + domain
        replymarks = get_param('mail.replyto.alias',
                               default=DEFAULT_REPLYTO_PREFIX)
        prefixes = [alias.strip() + '+' for alias in replymarks.split(',')]
        found, model, thread_id = None, None, None
        Threads = obj.env['mail.thread']
        matches = None
        while not found and recipients:
            res = recipients.pop(0)
            if any(res.startswith(p) and res.endswith(domain) for p in prefixes):
                matches = res
                thread_index = res[res.find('+') + 1:res.find('@')]
                model, thread_id = Threads._threadref_by_index(thread_index)
                found = bool(model and thread_id)
        if not found and matches:
            # It matches a unique address format but thread not found.  Lets
            # provide a route that allow to process the message properly.
            # Also sender will be notified that the address given is no longer
            # valid.
            return (BOUNCE_ROUTE_MODEL, None)
        return (model, thread_id) if found else None

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        def valid(route):
            # A valid route is one that does not shadow our Reply-to and does
            # not create a new thread (the classical fallback to crm.lead)
            return route[0] != model and bool(route[1])
        model, thread_id = data
        # Must change the current `routes` **in-place**.
        routes[:] = [route for _pos, route in cls.find_route(routes, valid)]
        # TODO: Find the true user_id
        routes.append((model, thread_id, dict(original_message=message), SUPERUSER_ID, None))
        return routes
