#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.transporter
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

'''A transport to add a unique Return-Path to each outbound message.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.addons.xopgi_mail_threads import MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData

from . import verpcoder


class VERPTransport(MailTransportRouter):
    '''A Variable Envelop Return Path Transport.

    Along with the router takes care of matching outgoing messages with
    bounces.

    Done via a VERP scheme.

    '''
    def _get_bounce_address(self, obj, cr, uid, mail_id, model_name,
                            thread_id, email_to, context=None):
        '''Compute the bounce address.

        The bounce address is used to set the envelop address if no envelop
        address is provided in the message.  It is formed by properly joining
        the `bounce alias <.common.get_bounce_alias>`:func: the id, model,
        res_id of mail.mail object.

        :param mail_id: The id of the mail.mail object being sent.

        :param model_name: This is the model name of the OpenERP object
                           issuing the message.  Since the messaging system in
                           OpenERP is a mixin, this could be a task, lead,
                           invoice, etc..

        :param thread_id: The id of the object where this message is being
                          sent from.

        :param email_to: The address to which the message is being sent.

        If "mail.catchall.domain" is not set, return None.

        .. warning:: This have a weakness, if an mail is sent and, for any
           reason, not saved on db the possible bounded messages could not be
           related with the recipient.

        '''
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
        if mail_id:
            if model_name and thread_id:
                return '%s-%d-%s-%d+%s@%s' % (
                    postmaster, mail_id, model_name, thread_id, email_to,
                    domain)
            else:
                return '%s-%d+%s@%s' % (postmaster, mail_id, email_to,
                                        domain)
        else:
            return '%s@%s' % (postmaster, domain)

    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        '''Apply on both OpenERP 7 and Odoo for any outbound message,
        if context have mail_id key.

        '''
        context = context if context else {}
        return context.get('mail_id', False)

    def prepare_message(self, obj, cr, uid, message, context=None):
        '''Add the bounce address to the message.

        '''
        mail_id = context.get('mail_id', False) if context else False
        mail = obj.pool['mail.mail'].browse(cr, uid, mail_id, context=context)
        del message['Return-Path']  # Ensure a single Return-Path
        message['Return-Path'] = self._get_bounce_address(
            obj,
            cr,
            uid,
            mail.id,
            mail.model,
            mail.res_id,
            mail.email_to or message['To'],
            context=context
        )
        return TransportRouteData(message, {})
