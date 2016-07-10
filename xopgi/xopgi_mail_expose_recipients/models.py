#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_cc_save.models
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-07-06

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models
from openerp.tools.mail import email_split_and_format
from xoeuf.osv.orm import get_modelname

try:
    # Odoo 8
    from openerp.addons.mail.mail_thread import mail_thread, decode_header
    from openerp.addons.mail.mail_message import mail_message
except ImportError:
    # Odoo 9 fallback
    from openerp.addons.mail.models.mail_thread import mail_thread, decode_header
    from openerp.addons.mail.models.mail_message import mail_message


class MailMessage(models.Model):
    _name = get_modelname(mail_message)
    _inherit = _name

    recipients = fields.Char()


class MailThread(models.Model):
    _name = get_modelname(mail_thread)
    _inherit = _name

    @api.model
    def message_parse(self, message, save_original=False):
        result = super(MailThread, self).message_parse(
            message, save_original=save_original)
        # Save all original recipients on mail message cc field.
        raw_recipients = []
        for header in ('To', 'Cc', 'Delivered-To', 'Resent-To',
                       'Resent-Cc', 'Envelop-To'):
            raw_recipients.append(decode_header(message, header))
        recipients = []
        for recipient in raw_recipients:
            recipients.extend(email_split_and_format(recipient))
        result['recipients'] = ', '.join(recipients)
        return result
