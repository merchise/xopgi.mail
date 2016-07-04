# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xhg_ca_coordination_board.reports.confirmation_time
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2016-06-18

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models


class MailGroup(models.Model):
    _inherit = 'mail.group'

    enable_auto_subscribe = fields.Boolean(default=False,
                                           string='Enable automatic subscription',
                                           help='''If checked, this group will
                                                   not auto subscribe mail
                                                   senders''')

    @api.model
    def create(self, vals):
        # INFO: Disable author auto following if asked
        if self.enable_auto_subscribe:
            self = self.with_context(mail_create_nosubscribe=True)
        return super(MailGroup, self).create(vals)
