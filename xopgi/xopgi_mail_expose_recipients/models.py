#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, fields, models

from xoeuf.models import get_modelname
from xoeuf.models.proxy import MailMessage as Message

from xoeuf.odoo.tools.mail import email_split_and_format
from xoeuf.odoo.addons.xopgi_mail_threads.utils import decode_header


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
