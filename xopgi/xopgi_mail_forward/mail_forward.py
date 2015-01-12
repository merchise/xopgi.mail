#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.mail_forward
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


from openerp.osv import fields, orm
from openerp.tools.translate import _


class mail_compose_forward(orm.TransientModel):
    """Allow forwarding a message.

    It duplicates the message and optionally attaches it to another object of
    the database and sends it to another recipients than the original one.

    """

    # TODO:  Use xouef's get_modelname
    _name = str('mail.compose.forward')
    _inherit = str('mail.compose.message')

    _models = [
        'crm.lead',
        'crm.meeting',
        'crm.phonecall',
        'mail.group',
        'note.note',
        'product.product',
        'project.project',
        'project.task',
        'res.partner',
        'sale.order',
    ]

    def models(self, cr, uid, context=None):
        """Get allowed models and their names.

        It searches for the models on the database, so if modules are not
        installed, models will not be shown.

        """
        # TODO: Find modules that inherit from message
        context = context or dict()
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(
            cr, uid,
            [('model', 'in', context.get("model_list", self._models))],
            order="name",
            context=context
        )
        model_objs = model_pool.browse(cr, uid, model_ids, context=context)
        return [(m.model, m.name) for m in model_objs]

    _columns = {
        'destination_object_id': fields.reference(
            'Destination object',
            selection=models,
            size=128,
            help='Object where the forwarded message will be attached'
        ),

        # Override static relation table names in mail.compose.message
        'partner_ids': fields.many2many(
            'res.partner',
            string='Additional contacts'
        ),

        'attachment_ids': fields.many2many(
            'ir.attachment',
            string='Attachments'
        ),
    }

    def default_get(self, cr, uid, fields, context=None):
        result = super(mail_compose_forward, self).default_get(
            cr, uid, fields, context=context
        )

        result['subject'] = (
            result.get('subject') or context.get('default_subject')
        )

        if 'destination_object_id' in result:
            model, id = result['destination_object_id'].split(',')
            name = self.pool.get(model).name_get(
                cr, uid, int(id), context=context
            )[0][1]

            result['record_name'] = name
            if not result['subject']:
                result['subject'] = _('FWD') + ': ' + name
        return result
