# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.ir_mail_server
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

from openerp.addons.mail.mail_thread import decode_header, mail_header_msgid_re
from openerp.addons.xopgi_mail_threads import MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData
from .common import message_id_is_encoded


class OriginalReferenceTransport(MailTransportRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        ''' If Message-ID or any reference is encoded decode and add it to
        References to allow correct threading.

        '''
        references = mail_header_msgid_re.findall(
            decode_header(message, 'References') or '')
        iter_references = references + [message.get('Message-ID')]
        result = False
        if iter_references:
            for ref in iter_references:
                original_ref = message_id_is_encoded(obj, cr, uid, ref)
                if original_ref and original_ref not in references:
                    references.append(original_ref)
                    result = True
        return result, dict(references=' '.join(references))

    def prepare_message(self, obj, cr, uid, message, data=None, context=None):
        '''Replace message References by query method data result.

        '''
        del message['References']
        message['References'] = data['references']
        return TransportRouteData(message, {})