#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.mail_forward
# --------------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
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
                        print_function as _py3_print)

from lxml import html
from xoutil.string import cut_prefixes

try:
    from openerp import models, api
    from openerp.tools.translate import _
except ImportError:
    from odoo import models, api
    from odoo.tools.translate import _


class ForwardMail(models.TransientModel):
    """Allow forwarding a message.

    It duplicates the message and optionally attaches it to another object of
    the database and sends it to another recipients than the original one.

    """
    _name = 'mail.compose.message'
    _inherit = _name

    @api.model
    def default_get(self, fields):
        result = super(ForwardMail, self).default_get(fields)
        result['subject'] = (
            self._context.get('default_subject') or result.get('subject')
        )
        # Fix unclosed HTML tags.
        body = result.get('body', '')
        if body:
            result['body'] = html.tostring(html.document_fromstring(body))
        model = self._context.get('default_model', None)
        res_id = self._context.get('default_res_id')
        if model and res_id:
            name = self.env[model].browse(int(res_id)).name_get()[0][1]
            result['record_name'] = name
            if not result['subject']:
                result['subject'] = _('Fwd:') + cut_prefixes(
                    name, _('Re:'), _('Fwd:')
                )
        return result
