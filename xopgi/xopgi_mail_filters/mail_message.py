#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi.mail.xopgi_mail_filters.mail_message
# --------------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


try:
    from odoo import fields, models
    from odoo.addons.mail.models.mail_message import Message as mail_msg
except ImportError:
    from openerp import fields, models
    from openerp.addons.mail.mail_message import mail_message as mail_msg

from xoeuf import api
from xoeuf.models import get_modelname


def translate_model_name(self, model):
    """Translate the `text` into language codes.

    :param model: Model name like 'crm.partner'

    :return: A list of different possible translations of `model` name.

    """
    model_names = {
        m.name
        for m in self.env['ir.model'].search([('model', '=', model)])
    }
    ir_translation = self.env['ir.translation']
    translations = {
        t.value
        for t in ir_translation.search([
            ('name', '=', 'ir.model,name'),     # Search in model names only
            ('src', 'in', model_names),         # Search for model name
            ('state', '=', 'translated'),       # Search a translated name
        ])
    }
    return list(translations.union(model_names))


class mail_message(models.Model):
    """Store the translated name of the model that the message reference to."""

    _name = _inherit = get_modelname(mail_msg)

    model_names = fields.Char(
        compute='_get_model_names',
        search='_search_model_names',
        string='Associated to',
    )

    @api.multi
    def _get_model_names(self):
        for message in self:
            if message.model:
                translations = translate_model_name(
                    self,
                    message['model'],
                )
                message.model_names = ' | '.join(translations)

    @api.model
    def _search_model_names(self, operator, value):
        ir_translation = self.env['ir.translation']
        translations = ir_translation.search(
            [
                ('name', '=', 'ir.model,name'),     # Search in model names
                '|',                                # If any of:
                ('src', operator, value),           # source matches value
                ('value', operator, value),         # translation matches value
            ],
        )
        model_names = list({trans.src for trans in translations})
        models = [
            m.model
            for m in self.env['ir.model'].search([('name', 'in', model_names)])
        ]
        return [('model', 'in', models)]
