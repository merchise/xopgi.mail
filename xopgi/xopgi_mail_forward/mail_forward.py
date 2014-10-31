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
from xoutil.iterators import first_non_null as first


class MailComposeForward(orm.TransientModel):
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

        'move_attachments': fields.boolean(
            'Move attachments',
            help='Attachments will be assigned to the chosen destination '
                 'object and you will be able to pick them from its '
                 '"Attachments" button, but they will not be there for '
                 'the current object if any. In any case you can always '
                 'open it from the message itself.'
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

    def onchange_destination_object_id(self, cr, uid, ids,
                                       destination_object_id, context=None):
        """Update some fields for the new message."""
        context = context or dict()
        model = res_id = res_name = False

        if destination_object_id:
            model, res_id = destination_object_id.split(str(','))
            res_id = int(res_id)

            context['model_list'] = context.get('model_list', [model])
            model_name = dict(self.models(cr, uid, context=context)).get(model)
            _, res_name = first(
                self.pool.get(model).name_get(cr, uid, res_id, context=context)
            )
            if model_name:
                res_name = "%s %s" % (model_name, res_name)

        return {
            'value': {
                'model': model,
                'res_id': res_id,
                'record_name': res_name
            },
        }

    def send_mail(self, cr, uid, ids, context=None):
        """Send mail, execute the attachment relocation if needed."""
        result = super(MailComposeForward, self).send_mail(
            cr, uid, ids, context=context
        )

        # Attachment relocation if needed.
        ir_attachment = self.pool.get('ir.attachment')
        for wz in self.browse(cr, uid, ids, context=context):
            if (wz.move_attachments and
                    wz.model and
                    wz.res_id and
                    wz.attachment_ids):
                ir_attachment.write(
                    cr,
                    uid,
                    [att.id for att in wz.attachment_ids],
                    {'res_model': wz.model, 'res_id': wz.res_id},
                    context=context
                )
        return result
