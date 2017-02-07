# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_move_copy_msg_commons.mail_config
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-07-11

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models


class MailConfig(models.Model):
    _inherit = 'base.config.settings'

    default_views = fields.Many2many(
        'xopgi.selectable.view',
        default=lambda self: self.env['xopgi.selectable.view'].search([]))

    @api.multi
    def execute(self):
        result = super(MailConfig, self).execute()
        self.default_views.search(
            [('id', 'not in', self.default_views.ids)]).unlink()
        return result
