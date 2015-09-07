# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.mail_message
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-02
''' Avoid insert duplicated message_id on db.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.models import Model
from .common import encode_message_id


class MailMessage(Model):
    _inherit = str('mail.message')

    def create(self, cr, uid, values, context=None):
        context = dict(context or {})
        message_id = values.get('message_id', False)
        if message_id and self.search(
                cr, uid, [('message_id', '=', message_id)], count=True):
            values['message_id'] = encode_message_id(self, cr, uid, message_id)
        id = super(MailMessage, self).create(cr, uid, values, context=context)
        return id

    def copy(self, cr, uid, id, default=None, context=None):
        if 'message_id' not in default:
            msg = self.browse(cr, uid, id, context=context)
            default['message_id'] = encode_message_id(self, cr, uid,
                                                      msg.message_id)
        return super(MailMessage, self).copy(cr, uid, id, default,
                                             context=context)
