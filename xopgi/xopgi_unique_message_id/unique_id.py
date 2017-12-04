#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Avoid insert duplicated message_id on db.

Problem: When a message is received and routed to several objects it gets
duplicated.  Transports may then have trouble trying to find the unique
message they are delivering if they find more than one message with the same
Message-Id in the DB.

This addon will ensure that newly created messages have unique ids.  We simply
search for a clash and enumerate them.

In order for this to work we must also re-insert the original Message-Id when
delivering a mail, so that the user may related to the original message.  We
send both Message-Ids so that replies (containing both ids) are properly
found.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, models
from xoeuf.odoo.addons.xopgi_mail_threads import MailTransportRouter
from xoeuf.odoo.addons.xopgi_mail_threads import TransportRouteData
from xoeuf.odoo.addons.xopgi_mail_threads.utils import decode_header
from xoeuf.odoo.addons.base.ir.ir_mail_server import encode_header

try:
    from xoeuf.odoo.tools import mail_header_msgid_re
except ImportError:
    try:
        from xoeuf.odoo.addons.mail.mail_thread \
            import mail_header_msgid_re
    except ImportError:
        from xoeuf.odoo.addons.mail.models.mail_thread \
            import mail_header_msgid_re

from .common import message_id_is_encoded, encode_message_id


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        message_id = values.get('message_id', False)
        if message_id and self.search([('message_id', '=', message_id)]):
            values['message_id'] = encode_message_id(self, message_id)
        return super(MailMessage, self).create(values)


class MailThread(models.AbstractModel):
    _name = str('mail.thread')
    _inherit = _name

    @api.model
    def message_route(self, message, message_dict, model=None,
                      thread_id=None, custom_values=None):
        ''' Remove original Message-ID if message References has both
        original and encoded.

        It only happen when is replying a message treated on
        OriginalReferenceTransport implemented on this module.

        '''
        # This better here and not on a Router to remove unwanted references
        # before super's message_route call, or else it is possible to get a
        # wrong route and miss the right one.
        references = decode_header(message, 'References')
        thread_references = references or ''
        msg_references = mail_header_msgid_re.findall(thread_references)
        if msg_references and len(msg_references) > 1:
            result_references = msg_references[:]
            for ref in msg_references:
                original_ref = message_id_is_encoded(self, ref)
                if original_ref and original_ref in references:
                    result_references.remove(original_ref)
            del message['References']
            message['References'] = ' '.join(result_references)
        result = super(MailThread, self).message_route(
            message, message_dict, model=model, thread_id=thread_id,
            custom_values=custom_values
        )
        return result


class OriginalReferenceTransport(MailTransportRouter):
    @classmethod
    def query(cls, obj, message):
        ''' If Message-ID or any reference is encoded decode and add it to
        References to allow correct threading.

        '''
        references = mail_header_msgid_re.findall(
            decode_header(message, 'References') or '')
        iter_references = references + [message.get('Message-ID')]
        result = False
        if iter_references:
            for ref in iter_references:
                original_ref = message_id_is_encoded(obj, ref)
                if original_ref and original_ref not in references:
                    references.append(original_ref)
                    result = True
        return result, dict(references=' '.join(references))

    def prepare_message(self, obj, message, data=None):
        '''Replace message References by query method data result.

        '''
        del message['References']
        message['References'] = encode_header(data['references'])
        return TransportRouteData(message, {})
