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


from openerp.osv import fields, osv
from openerp.addons.mail.mail_message import mail_message as mail_msg
from xoeuf.osv.orm import get_modelname
from xoeuf.osv.model_extensions import search_value, search_read


def translate_model_name(pool, cr, uid, model, context=None):
    """Translate the `text` into language codes.

    :param model: Model name like 'crm.partner'

    :return: A list of different possible translations of `model` name.

    """
    model_names = search_value(
        pool.get('ir.model'), cr, uid,
        [('model', '=', model)],
        'name'
    )
    model_names = (
        model_names.values() if isinstance(model_names, dict) else [model_names]
    )
    ir_translation = pool.get('ir.translation')
    translations = search_value(
        ir_translation, cr, uid,
        [
            ('name', '=', 'ir.model,name'),     # Search in model names only
            ('src', 'in', model_names),         # Search for model name
            ('state', '=', 'translated'),       # Search a translated name
        ],
        'value',
        context=context
    )
    translations = set(
        translations.values()
        if isinstance(translations, dict)
        else [translations]
    )
    return list(translations.union(set(model_names)))


class mail_message(osv.Model):
    """Store the translated name of the model that the message reference to."""

    _name = get_modelname(mail_msg)
    _inherit = get_modelname(mail_msg)

    def _get_model_names(self, cr, uid, ids, name, args=None, context=None):
        result = {}
        messages = self.read(
            cr, uid, ids=ids, fields=['model'], context=context
        )
        for message in messages:
            names = ''
            if message['model']:
                translations = translate_model_name(
                    self.pool, cr, uid,
                    message['model'],
                    context=context
                )
                names = ' | '.join(translations)
            result[message['id']] = names
        return result

    def _search_model_names(self, cr, uid, obj, name, args, context=None):
        field, operator, value = args[0]
        ir_translation = self.pool.get('ir.translation')

        translations = search_read(
            ir_translation, cr, uid,
            [
                ('name', '=', 'ir.model,name'),     # Search in model names
                '|',                                # If any of:
                ('src', operator, value),           # source matches value
                ('value', operator, value),         # translation matches value
            ],
            fields=['src', 'value'],
            context=context
        )
        model_names = list(set(trans['src'] for trans in translations))
        models = search_value(
            self.pool.get('ir.model'),
            cr, uid, [('name', 'in', model_names)], 'model'
        )
        models = models.values() if isinstance(models, dict) else [models]
        return [('model', 'in', models)]

    _columns = {
        'model_names': fields.function(
            _get_model_names,
            fnct_search=_search_model_names,
            string='Associated to',
            type='char',
        ),
    }
