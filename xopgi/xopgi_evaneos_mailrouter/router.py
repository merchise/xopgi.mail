#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A MailRouter for messages delivered via Evaneos MTA.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
from email.utils import getaddresses, formataddr
from re import compile as _re_compile
from xoutil.future.itertools import map

from xoeuf.odoo.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from xoeuf.odoo.addons.base.ir.ir_mail_server import encode_rfc2822_address_header  # noqa


logger = logging.getLogger(__name__)


class MATCH_TYPE:
    SENDER = 0
    RECIPIENT = 1


class EvaneosMail(object):
    @classmethod
    def get_addresses_headers(cls, msg, headers):
        result = []
        get = msg.get_all
        for header in headers:
            result.extend(getaddresses(get(header, [])))
        return result

    @classmethod
    def get_senders_addresses(cls, msg):
        # The X-Original-From is because we may (or may not) have already
        # changed the From to another address.  Any addon that changes the
        # From should keep the previous From in the X-Original-From.
        headers = ['Sender', 'From', 'X-Original-From']
        return [
            email
            for _, email in cls.get_addresses_headers(msg, headers)
        ]

    @classmethod
    def get_recipients(cls, msg):
        return cls.get_addresses_headers(msg, ['To', 'Cc', 'Bcc'])

    @classmethod
    def get_recipients_addresses(cls, msg):
        headers = ['To', 'Cc', 'Bcc']
        return [
            email
            for _, email in cls.get_addresses_headers(msg, headers)
        ]

    @classmethod
    def get_evaneos_regexp(cls, obj):
        config = obj.env['ir.config_parameter']
        pattern = config.get_param(
            'evaneos.mailrouter.pattern',
            # The default allows to tests pass.
            default=r'_(?P<thread>\d+)(?P<uuid>[_-][^@]+)?(?P<host>@.*(?<=['
                    r'@\.])evaneos\.com)$ '
        )
        return _re_compile(pattern)

    @classmethod
    def get_all_matches(cls, obj, message, matchtype=MATCH_TYPE.SENDER):
        if matchtype is MATCH_TYPE.SENDER:
            addresses = cls.get_senders_addresses(message)
        elif matchtype is MATCH_TYPE.RECIPIENT:
            addresses = cls.get_recipients(message)
        else:
            raise ValueError('Invalid match type %r' % matchtype)
        search = cls.get_evaneos_regexp(obj).search
        return (match for match in map(search, addresses) if match)

    @classmethod
    def get_first_match(cls, obj, message, matchtype=MATCH_TYPE.SENDER):
        return next(
            cls.get_all_matches(obj, message, matchtype=matchtype),
            None
        )


class EvaneosMailTransport(EvaneosMail, MailTransportRouter):
    # Don't send the emails coming from Evaneos to any other Evaneos address
    @classmethod
    def query(cls, obj, message):
        sender = cls.get_first_match(obj, message, matchtype=MATCH_TYPE.SENDER)
        recipient = cls.get_first_match(obj, message, matchtype=MATCH_TYPE.RECIPIENT)
        return bool(sender and recipient), None

    def prepare_message(self, obj, message, data=None):
        # Remove all Evaneos recipients.  Treat each header separately
        search = self.get_evaneos_regexp(obj).search
        for header in ['To', 'Cc', 'Bcc']:
            recipients = [
                (name, email)
                for name, email in self.get_addresses_headers(message, [header])
                if not search(email)
            ]
            del message[header]
            if recipients:
                message[header] = encode_rfc2822_address_header(
                    ', '.join(formataddr(address) for address in recipients)
                )

    def deliver(self, server, message, data, **kwargs):
        recipients = self.get_recipients(message)
        if recipients:
            return super(EvaneosMailTransport, self).deliver(
                server,
                message,
                data,
                **kwargs
            )


class EvaneosMailRouter(EvaneosMail, MailRouter):
    @classmethod
    def query(cls, obj, message):
        match = cls.get_first_match(obj, message)
        return bool(match), match

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        match = data
        sender = match.group(0)
        fmodel, fthread = 0, 1
        escape = lambda s: s.replace('_', r'\_').replace('%', r'\%')
        # Create canonical address for search. When the first non-canonical mail
        # arrives, the previous one has a canonical address and that's the one we
        # should looking for.
        regexp = cls.get_evaneos_regexp(obj)
        dossier = regexp.search(sender)
        canonical_sender = dossier.group('thread') + dossier.group('host')
        # The query for any email from the same sender that has a resource id,
        # but its parent has no parent:  Explanation:  When a new message from
        # Evaneos arrives OpenERP actually creates two messages: A
        # Notification for the recently created Lead and the original
        # message.  Strangely enough, the notification is the "parent" of the
        # message that actually started everything.
        #
        # The query is in prefix notation, but some ANDs are omitted since
        # they are implied.
        query = [
            '|',
            '|',
            '|',
            ('email_from', '=like', "%%%s" % escape(sender)),   # Ends with _XXX@..
            ('email_from', '=like', '%%%s>' % escape(sender)),  # or _XXX@..>
            ('email_from', '=like', "%%%s" % escape(canonical_sender)),
            ('email_from', '=like', '%%%s>' % escape(canonical_sender)),

            ('parent_id.parent_id', '=', None),
            ('res_id', '!=', 0),
            ('res_id', '!=', None)
        ]
        mail_message = obj.env['mail.message']
        result = mail_message.search(query)
        if result:
            result = result[0] if len(result) > 1 else result
            model = result.model
            thread_id = result.res_id
            # Find the matching route. The matching route is the first its
            # model is the same as the one found in the root message and
            # its thread id is not set (i.e would create a new
            # conversation).
            pred = lambda r: (r[fmodel] == model and
                              (not r[fthread] or r[fthread] == thread_id))
            i, route = next(cls.find_route(routes, pred), (None, None))
            if route:
                routes[i] = (model, thread_id, ) + route[2:]
            else:
                # Odoo routes are 5-tuple.  The last is the alias
                # record.  Best not to pass any.
                routes.append((model, thread_id, {}, obj._uid, None))
