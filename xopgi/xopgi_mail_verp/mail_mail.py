# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api

try:
    from odoo import models
except ImportError:
    from openerp import models


class Mail(models.Model):
    '''Override the send method to add mail_id on context.

    This is needed by the transport to properly build a bounce address which
    include the id of the mail_mail object and since a single mail_mail is
    create for each recipient of the message, any of which can bounce.

    Transports are only provided with the `message`, but we need to know which
    recipient is bouncing.  That's why we serialize the sending in a way that
    `send_email` is called with the "mail_id" in the `context`, which is then
    inspected by our transport.

    '''

    _name = 'mail.mail'
    _inherit = _name

    @api.multi
    def send(self, *args, **kwargs):
        # Add mail_id to context and call _super one by one.
        #
        # verp_mail_id may use to get unique return-path.
        if len(self) > 1:
            res = True
            for record in self:
                res = self.browse(record.id).with_context(
                    verp_mail_id=record.id
                ).send(*args, **kwargs) and res
        else:
            res = super(Mail, self.with_context(
                verp_mail_id=self.id
            )).send(*args, **kwargs)
        return res
