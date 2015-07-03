# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.mail_thread
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-02

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)
from openerp.osv.orm import AbstractModel
from openerp.addons.mail.mail_thread import decode_header, mail_header_msgid_re
from .common import message_id_is_encoded


class MailThread(AbstractModel):
    _name = str('mail.thread')
    _inherit = _name

    def message_route(self, cr, uid, message, message_dict, model=None,
                      thread_id=None, custom_values=None, context=None):
        ''' Remove original Message-ID if message References has both
        original and encoded.

        It only happen when is replying a message treated on
        IrMailServer.send_email() method implemented on this module.

        '''
        references = decode_header(message, 'References')
        thread_references = references or ''
        msg_references = mail_header_msgid_re.findall(thread_references)
        if msg_references and len(msg_references) > 1:
            result_references = msg_references[:]
            for ref in msg_references:
                original_ref = message_id_is_encoded(self, cr, uid, ref)
                if original_ref and original_ref in references:
                    result_references.remove(original_ref)
            del message['References']
            message['References'] = ' '.join(result_references)
        result = super(MailThread, self).message_route(
            cr, uid, message, message_dict, model=model, thread_id=thread_id,
            custom_values=custom_values, context=context)
        return result
