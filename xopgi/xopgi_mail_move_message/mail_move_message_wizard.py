# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10
from openerp.osv import osv, fields
from openerp.tools.translate import _


class MoveMessageWizard(osv.TransientModel):
    _name = 'move.message.wizard'

    _columns = {
        'thread_id':
            fields.reference('Destination Mail Thread', selection=(
                lambda s, u, c, ctx:
                                          s.pool['mail.thread'].message_capable_models(
                                          c, u, context=ctx).items()),
                                      size=128, required=True),
        'message_ids': fields.many2many('mail.message', 'message_move_rel',
                                        'move_id', 'message_id',
                                        'Messages', readonly=True),
        'leave_msg':
            fields.boolean('Preserve original messages',
                           help="Check for no remove message from original "
                                "thread."),
    }

    _defaults = {
        'leave_msg': True
    }

    def default_get(self, cr, uid, fields_list, context=None):
        values = super(MoveMessageWizard, self).default_get(
            cr, uid, fields_list, context=context)
        if 'message_ids' in fields_list:
            values['message_ids'] = context.get('active_ids', [])
        return values

    def confirm(self, cr, uid, ids, context=None):
        '''Create a new mail thread, remove original message if not
        leave_msg  and open new thread on edit form.

        '''
        wiz = self.browse(cr, uid, ids[0], context=context)
        msg_obj = self.pool['mail.message']
        model = wiz.thread_id._name
        res_id = wiz.thread_id.id
        values = {'model': model, 'res_id': res_id}
        if wiz.leave_msg:
            for msg in wiz.message_ids:
                msg_obj.copy(cr, uid, msg.id, values, context=context)
        else:
            msg_obj.write(cr, uid, wiz.message_ids._ids, values,
                          context=context)
        return {
            'name': _('Copy/Move Messages'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'res_id': res_id,
            'type': 'ir.actions.act_window',
            'context': dict(context or {}, active_id=res_id)
        }
