#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.mail_forward
# --------------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
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

from openerp.osv import orm
from openerp.tools.translate import _


class mail_compose_forward(orm.TransientModel):
    """Allow forwarding a message.

    It duplicates the message and optionally attaches it to another object of
    the database and sends it to another recipients than the original one.

    """

    # TODO:  Use xouef's get_modelname
    _name = 'mail.compose.message'
    _inherit = _name

    def default_get(self, cr, uid, fields, context=None):
        result = super(mail_compose_forward, self).default_get(
            cr, uid, fields, context=context
        )
        result['subject'] = (
            result.get('subject') or context.get('default_subject')
        )
        # Fix unclosed HTML tags.
        body = result.get('body', '')
        if body:
            result['body'] = html.tostring(html.document_fromstring(body))
        model = context.get('default_model', None)
        res_id = context.get('default_res_id')
        if model and res_id:
            name = self.pool[model].name_get(
                cr, uid, [int(res_id)], context=context
            )[0][1]
            result['record_name'] = name
            if not result['subject']:
                result['subject'] = _('Fwd:') + cut_prefixes(
                    name, _('Re:'), _('Fwd:')
                )
        return result

    def send_mail(self, cr, uid, ids, context=None):
        super(mail_compose_forward, self).send_mail(cr, uid, ids,
                                                    context=context)
        return {'type': 'ir.actions.client', 'tag': 'reload', }
"""
{"default_attachment_ids": [],
"default_model":
   "project.task",
"default_res_id": 3488,
"default_subject": "Fwd: "
                  "RE: "
                  "EDUCTOUR VDM 2015"

{
"default_parent_id": 61947,
"default_attachment_ids": [],

"default_partner_ids": [],
"default_is_log": false,
"mail_post_autofollow":
   true,
"mail_post_autofollow_partner_ids": [],
"is_private": false

"""