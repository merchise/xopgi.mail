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


class MailConfig(models.TransientModel):
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
