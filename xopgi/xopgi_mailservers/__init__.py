#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mailservers
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-22

'''A transport that tries to send a message using an SMTP server that
"matches" the original receiver of the first message in the thread.

This works like this:

- You may have several registered SMTP servers and also several matching
  incoming servers (though optional).

- Suppose you have an SMTP server that connects identifies itself (SMTP
  authentication) with "john.doe@gamil.com".

- You receive a message To: john.doe@gamil.com.  That creates a new thread
  (say a CRM lead).

- Then when responding to that thread, we'll choose the SMTP server that
  matches (one of) the recipients of the original message that created the
  thread.

  Also the From address of the message will be set to that of the outgoing
  SMTP server.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil import logger as _logger

from openerp.osv.orm import Model
from openerp.osv import fields

from openerp.addons.xopgi_mail_threads import MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData


class MailServer(Model):
    # Adds the delivered column
    _inherit = 'ir.mail_server'

    _columns = {
        'delivered_address':
            fields.char(
                'Delivered to',
                required=False,
                help=('The email address that should be check as the '
                      'recipient of this server.  This way we can match this '
                      'server for outgoing messages in response to emails '
                      'delivered to this address.'),
            ),
    }


class SameOriginTransport(MailTransportRouter):
    @classmethod
    def servers(cls, obj, cr, uid):
        from openerp import SUPERUSER_ID
        from xoeuf.osv.model_extensions import search_browse
        servers = obj.pool['ir.mail_server']
        query = [('delivered_address', '!=', None)]
        found = search_browse(servers, cr, SUPERUSER_ID, query)
        return found

    @classmethod
    def query(self, obj, cr, uid, message, context=None):
        return bool(self.servers(obj, cr, uid))

    def prepare_message(self, obj, cr, uid, message, context=None):
        import email
        from xoutil.string import safe_encode
        _, refs = self.get_message_objects(obj, cr, uid, message,
                                           context=None)
        connection_data = {}
        if refs:
            # It seems OpenERP always uses the "original" message-id in the
            # references.  At least, for outgoing messages.
            parent = refs[0]
            mail = email.message_from_string(safe_encode(parent.raw_email))
            server = self.origin_server(obj, cr, uid, mail)
            originators = self.get_authors(mail, msg=parent)
            recipients = self.get_recipients(message)
            # Only use this server for messages going to the originators,
            # i.e the authors of the parent email.
            if server and (set(recipients) & set(originators)):
                _logger.info(
                    'SMTP outgoing server %s will send message %s',
                    server.name,
                    message['Message-Id'],
                )
                connection_data.update(mail_server_id=server.id)
                address = server.delivered_address
                # Ensure the Return-Path is used for the envelop and
                # matches the Sender (not necessarily the From).  The
                # Reply-To also changes, it is assumed you'll have a
                # matching POP/IMAP incoming fetchmail server for the same
                # account.
                del message['Reply-To'], message['Sender']
                message['Return-Path'] = message['Sender'] = address
                message['Reply-To'] = address
            else:
                _logger.info(
                    'Default SMTP server for message %s, going to %s',
                    message['Message-Id'],
                    recipients,
                )
        return TransportRouteData(message, connection_data)

    def get_authors(self, message, msg=None):
        from email.utils import getaddresses
        if msg and msg.email_from:
            authors = getaddresses([msg.email_from])
        elif message['From']:
            authors = getaddresses([message['From']])
        else:
            _logger.warn(
                'No From address for message %s', message['Message-Id']
            )
            authors = []
        return tuple(address for _, address in authors if address)

    def get_recipients(self, message):
        from email.utils import getaddresses
        recipients = getaddresses([
            message[header] or ''
            for header in ('To', 'Cc', 'Delivered-To')
        ])
        addresses = tuple({address for _, address in recipients if address})
        return addresses

    def origin_server(self, obj, cr, uid, message):
        '''Get the "origin" server for a message.'''
        from openerp import SUPERUSER_ID
        from xoeuf.osv.model_extensions import search_browse
        addresses = self.get_recipients(message)
        query = [('delivered_address', 'in', addresses)]
        servers = obj.pool['ir.mail_server']
        found = search_browse(servers, cr, SUPERUSER_ID, query,
                              ensure_list=True)
        return found[0] if found else None
