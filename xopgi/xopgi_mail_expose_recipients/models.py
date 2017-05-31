#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_cc_save.models
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
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

try:
    from openerp import api, fields, models
    from openerp.tools.mail import email_split_and_format
except ImportError:
    from odoo import api, fields, models
    from odoo.tools.mail import email_split_and_format


from xoeuf.osv.orm import get_modelname

try:
    from odoo.addons.mail.models.mail_message import Message
    from odoo.addons.xopgi_mail_threads.utils import decode_header
except ImportError:
    try:
        from openerp.addons.mail.mail_message import mail_message as Message
    except ImportError:
        from openerp.addons.mail.models.mail_message import Message
    from openerp.addons.xopgi_mail_threads.utils import decode_header


class MessageRecipients(models.Model):
    _name = get_modelname(Message)
    _inherit = _name

    recipients = fields.Char()


class MailThreadExpand(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = _name

    @api.model
    def message_parse(self, message, save_original=False):
        result = super(MailThreadExpand, self).message_parse(
            message, save_original=save_original
        )
        # Save all original recipients on mail message cc field.
        raw_recipients = []
        for header in ('To', 'Cc'):
            raw_recipients.append(decode_header(message, header))
        recipients = []
        for recipient in raw_recipients:
            recipients.extend(email_split_and_format(recipient))
        result['recipients'] = ', '.join(recipients)
        return result
