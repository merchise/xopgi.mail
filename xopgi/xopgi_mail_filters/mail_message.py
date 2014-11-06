#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi.mail.xopgi_mail_filters.mail_message
# --------------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Eddy Ernesto del Valle Pino <eddy@merchise.org>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


from xoutil.iterators import first_non_null as first
from xoutil.functools import lru_cache

from openerp.osv import fields, osv
from openerp.addons.mail.mail_message import mail_message as mail_msg
from xoeuf.osv.improve import integrate_extensions
from xoeuf.osv.orm import get_modelname


# WARNING: Don't do this in production code.  This is only meant to be used in
# shells.  Until shown that it does not do anything bad it's banned.  You must
# import the functions and provide all params.
integrate_extensions()


@lru_cache()
def translate(pool, cr, uid, text, lang_codes=(), name=None, context=None):
    """Translate the `text` into language codes.

    :param text: The text to translate.
    :param lang_codes: An iterable with the list of langauges to translate to.
    :param name: translation name

    :return: A dictionary {'lang_code': 'translation'}.

    """
    res_lang = pool.get('res.lang')
    ir_translation = pool.get('ir.translation')
    lang_codes = (
        lang_codes or
        [context.get('lang')] or
        res_lang.search_value(cr, uid, [], 'code').values()
    )
    translations = {code: text for code in lang_codes}
    for lang_code in lang_codes:
        domain = [
            ('lang', '=', lang_code),
            ('src', '=', text),
            ('state', '=', 'translated'),
        ]
        name_domain = domain + [('name', '=', name)] if name else domain
        ids = ir_translation.cascade_search(cr, uid, name_domain, domain)
        translation = ir_translation.field_value(cr, uid, ids, 'value')
        translation = (
            first(translation.values())
            if isinstance(translation, dict)
            else translation
        )
        if translation:
            translations[lang_code] = translation
    return translations


class mail_message(osv.Model):
    """Store the translated name of the model that the message reference to."""

    _name = get_modelname(mail_msg)
    _inherit = get_modelname(mail_msg)

    def _get_model_names(self, cr, uid, ids, name, args=None, context=None):
        result = {}
        ir_model = self.pool.get('ir.model')
        messages = self.read(
            cr, uid, ids=ids, fields=['model'], context=context
        )
        for message in messages:
            names = ''
            if message['model']:
                model_name = ir_model.search_value(
                    cr, uid, [('model', '=', message['model'])], 'name',
                    context=context,
                )
                names = translate(
                    self.pool, cr, uid, model_name, model=message['model'],
                    context=context,
                )
                names = ' | '.join(names.values())
            result[message['id']] = names
        return result

    def _search_model_names(self, cr, uid, obj, name, args, context=None):
        field, operator, value = args[0]
        ir_translation = self.pool.get('ir.translation')
        lang = context.get('lang')

        model_domain = ('name', '=', 'ir.model,name')
        source_domain = [('src', operator, value), model_domain]
        domain = [('value', operator, value), model_domain]
        lang_domain = domain + [('lang', '=', lang)] if lang else domain

        ids = ir_translation.cascade_search(
            cr, uid, lang_domain, source_domain, domain
        )
        translations = ir_translation.read(cr, uid, ids, fields=['src'])
        model_names = list(set(trans['src'] for trans in translations))

        models = self.pool.get('ir.model').search_value(
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
            readonly=True,
            stored=True,
            selectable=True,
        ),
    }
