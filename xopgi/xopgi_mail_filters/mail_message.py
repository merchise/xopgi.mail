#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#


from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print)

from xoeuf import fields, models, api
from xoeuf.models import get_modelname
from xoeuf.models.proxy import MailMessage


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

    _name = _inherit = get_modelname(MailMessage)

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
