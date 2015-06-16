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

'''
A MailRouter for bounced messages.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import re

from openerp import SUPERUSER_ID
from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData

from openerp.addons.mail.mail_thread import decode_header


from .mail_bounce_model import BOUNCE_MODEL
from . import verpcoder

# The way a thread reference was encoded before the global thread index was
# introduced:
#
# [model]-[thread-id]
#
CLASSICAL_REFERENCE_REGEX = re.compile(
    r'(?P<model>[\w\._\d]+)-(?P<thread_id>\d+)',
    re.UNICODE
)


# Regular expression for the trailing part of bounce address.
# You must have checked and stripped the "<bounce-alias>-" prefix.
#
# <message id>-<reference>+<encoded recipient>@<domain.com>
#
BOUNCE_ADDRESS_REGEXP = re.compile(
    r'(?P<messageid>\d+)-(?P<threadref>[^\+]+)\+(?P<failed_address>[^@]+)',
    re.UNICODE
)


class BouncedMailRouter(MailRouter):
    @classmethod
    def _message_route_check_bounce(self, obj, cr, uid, message):
        """Verify that the email_to is the bounce alias.

        """
        from xoutil.string import cut_prefix
        from .common import get_bounce_alias
        bounce_alias = get_bounce_alias(obj.pool, cr, uid)
        if not bounce_alias:
            return None
        prefix = bounce_alias + '-'
        recipient = decode_header(message, 'To')
        if not recipient.startswith(prefix):
            return None
        recipient = cut_prefix(recipient, prefix)
        matches = BOUNCE_ADDRESS_REGEXP.search(recipient)
        if matches:
            params = matches.groupdict()
            message_id = params['messageid']
            thread_ref = params['threadref']
            if thread_ref.startswith('#'):
                # This is the case of the global index introduced by us in our
                # Odoo build.
                thread_index = thread_ref[1:]
                Threads = obj.pool['mail.thread']
                model, thread_id = Threads._threadref_by_index(
                    cr, SUPERUSER_ID, thread_index
                )
            else:
                # Though new threads will have the global index, there may be
                # bounces in their way to us using the "classical" reference.
                matches = CLASSICAL_REFERENCE_REGEX.match(thread_ref)
                assert matches
                model, thread_id = matches.group(1, 2)
            failed_address = verpcoder.decode(params.get('failed_address', ''))
            return (message_id, model, int(thread_id), failed_address)
        else:
            return None

    @classmethod
    def _get_route(self, obj, cr, uid, bouncedata):
        return (BOUNCE_MODEL, bouncedata, {}, uid, None)

    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        route = cls._message_route_check_bounce(obj, cr, uid, message)
        return bool(route), route

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
        return routes


class VariableEnvReturnPathTransport(MailTransportRouter):
    '''A Variable Envelop Return Path Transport.

    Along with the router takes care of matching outgoing messages with
    bounces.

    Done via a VERP scheme.

    '''
    @classmethod
    def _get_bounce_address(cls, obj, cr, uid, message, mail, email_to,
                            context=None):
        '''Compute the bounce address.

        The bounce address is used to set the envelop address if no envelop
        address is provided in the message.  It is formed by properly joining
        the `bounce alias <.common.get_bounce_alias>`:func: the id, model,
        res_id of mail.mail object.

        :param message: The message (browse record) being sent.

        :param mail: The mail (browse record) being sent.

        The returned bounce address will always have the form::

           <postmaster>-<message id>-<reference>+<encoded recipient>@<domain.com>

        The reference will have one of the following forms:

        - ``#<global reference>`` if the thread has a global
          reference (i.e a unique identifier among all threads), that will
          never contain "+".

        - ``<model name>-<thread id>``

        '''
        if not mail.mail_message_id:
            # I can't provide a VERP bounce address without a message id.
            return None
        assert mail.mail_message_id == message
        from .common import get_bounce_alias
        get_param = obj.pool['ir.config_parameter'].get_param
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if not domain:
            return None
        if email_to:
            from six import string_types
            email_to = ([email_to] if isinstance(email_to, string_types)
                        else email_to)
            from email.utils import getaddresses
            email_to = getaddresses(email_to)
            # Get the address from first recipient (must be the unique one).
            email_to = email_to[0][-1] if email_to and email_to[0] else False
            email_to = verpcoder.encode(email_to) if email_to else ''
        postmaster = get_bounce_alias(obj.pool, cr, uid, context=context)
        message = mail.mail_message_id
        ref = getattr(message, 'thread_index', None)
        if ref:
            return '%s-%d-#%s+%s@%s' % (postmaster, message.id, ref, email_to,
                                        domain)
        if mail.model and mail.res_id:
            return '%s-%d-%s-%d+%s@%s' % (
                postmaster, message.id, mail.model, mail.res_id,
                email_to, domain)
        else:
            return '%s-%d+%s@%s' % (
                postmaster, message.id, email_to,
                domain)

    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        '''Apply on both OpenERP 7 and Odoo for any outbound message,
        if context have mail_id key.

        If applicable, return ``(True, {'address': address})``.

        '''
        context = context if context else {}
        mail_id = context.get('mail_id', False) if context else False
        if not mail_id:
            return False, None
        msg, _ = self.get_message_objects(obj, cr, uid, message,
                                          context=context)
        if msg:
            msg = msg[0] if isinstance(msg, list) else msg
            mail = obj.pool['mail.mail'].browse(cr, uid, mail_id,
                                                context=context)
            address = self._get_bounce_address(obj, cr, uid, msg, mail,
                                               mail.email_to or message['To'],
                                               context=context)
            return bool(address), dict(address=address)
        return False, None

    def prepare_message(self, obj, cr, uid, message, data=None, context=None):
        '''Add the bounce address to the message.

        '''
        del message['Return-Path']  # Ensure a single Return-Path
        message['Return-Path'] = data['address']
        return TransportRouteData(message, {})
