# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xhg_ca_coordination_board.reports.confirmation_time
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2016-07-05

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo import api, fields, models
except ImportError:
    from openerp import api, fields, models


class MailGroup(models.Model):
    _inherit = 'mail.group'

    enable_auto_subscribe = fields.Boolean(
        default=False,
        string='Enable automatic subscription',
        help='If checked, this group will auto subscribe mail senders'
    )

    @api.multi
    def message_post(self, **kwargs):
        nosubscribe = self.env.context.get('mail_create_nosubscribe')
        autofollow = self.env.context.get('mail_post_autofollow', True)
        overwritten = nosubscribe and not autofollow
        if not self.enable_auto_subscribe and not overwritten:
            _super = super(MailGroup, self.with_context(
                mail_create_nosubscribe=True,
                mail_post_autofollow=False
            ))
        else:
            _super = super(MailGroup, self)
        return _super.message_post(**kwargs)
