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

from openerp.release import version_info as ODOO_VERSION_INFO


class VERPTransport(MailTransportRouter):
    '''A Variable Envelop Return Path Transport.

    Along with the router takes care of matching outgoing messages with
    bounces.

    Done via a VERP scheme.

    '''
    def _get_bounce_address(self, obj, cr, uid, mail_id, model_name, res_id,
                            context=None):
        '''Compute the bounce address.

        The bounce address is used to set the envelop address if no
        envelop address is provided in the message.  It is formed by properly
        joining the parameters (`mail.catchall.alias` on openepr or
        `mail.bounce.alias` on odoo) and `mail.catchall.domain` with the
        id, model, res_id of mail.mail object.

        If `mail.catchall.alias` (openerp) or `mail.bounce.alias` (odoo) is
        not set it defaults to "postmaster-odoo".

        If "mail.catchall.domain" is not set, return None.

        .. warning:: This have a weakness, if an mail is sended and, for any
           reason, not saved on db the possible bounded messages could not be
           related with the recipient.

        '''
        from .common import get_bounce_alias
        postmaster = get_bounce_alias(obj.pool, cr, uid, context=context)
        get_param = obj.pool['ir.config_parameter'].get_param
        domain = get_param(cr, uid, 'mail.catchall.domain', context=context)
        if domain:
            if mail_id:
                if model_name and res_id:
                    return '%s-%d-%s-%d@%s' % (
                        postmaster, mail_id, model_name, res_id, domain)
                else:
                    return '%s-%d@%s' % (postmaster, mail_id, domain)
            else:
                return '%s@%s' % (postmaster, domain)
        else:
            return None

    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        '''Apply only in openerp 7, if mail_id is on context and message haven't
        Return-Path

        '''
        context = context if context else {}
        return (ODOO_VERSION_INFO < (8, 0) and context.get('mail_id', False)
                and not message.get('Return-Path'))

    def prepare_message(self, obj, cr, uid, message, context=None):
        '''Add the bounce address to the message.

        '''
        mail_id = context.get('mail_id', False) if context else False
        mail = obj.pool['mail.mail'].browse(cr, uid, mail_id, context=context)
        message['Return-Path'] = self._get_bounce_address(
            obj,
            cr,
            uid,
            mail.id,
            mail.model,
            mail.res_id,
            context=context
        )
        return TransportRouteData(message, {})
