#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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

from xoeuf import models, fields
from xoeuf.odoo.addons.xopgi_mail_threads import MailTransportRouter
from xoeuf.odoo.addons.xopgi_mail_threads import TransportRouteData

import logging
_logger = logging.getLogger(__name__)
del logging


class MailServer(models.Model):
    # Adds the delivered column
    _inherit = 'ir.mail_server'

    delivered_address = fields.Char(
        'Delivered to',
        required=False,
        help=('The email address that should be check as the '
              'recipient of this server.  This way we can match this '
              'server for outgoing messages in response to emails '
              'delivered to this address.'),
    )


class SameOriginTransport(MailTransportRouter):
    @classmethod
    def servers(cls, obj):
        servers = obj.env['ir.mail_server']
        query = [('delivered_address', '!=', None)]
        found = servers.sudo().search(query)
        return found

    @classmethod
    def query(self, obj, message):
        return bool(self.servers(obj))

    def prepare_message(self, obj, message, data=None):
        import email
        from xoutil.string import safe_encode
        _, refs = self.get_message_objects(obj, message)
        connection_data = {}
        if refs:
            # It seems OpenERP always uses the "original" message-id in the
            # references.  At least, for outgoing messages.
            parent = refs[0]
            mail = email.message_from_string(safe_encode(parent.raw_email))
            server = self.origin_server(obj, mail)
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
                message['Sender'] = address
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
                'No From address for message %s', message['Message-Id'],
                extra=dict(headers=dict(message.items()))
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

    def origin_server(self, obj, message):
        '''Get the "origin" server for a message.'''
        addresses = self.get_recipients(message)
        servers = obj.env['ir.mail_server']
        found = servers.sudo().search([('delivered_address', 'in', addresses)])
        return found[0] if found else None
