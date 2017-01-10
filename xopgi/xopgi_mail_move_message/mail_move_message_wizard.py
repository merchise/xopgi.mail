# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models, SUPERUSER_ID, _
from openerp.exceptions import AccessError
from openerp.addons.xopgi_move_copy_msg_commons.common import \
    get_model_selection

from xoeuf.ui import RELOAD_UI


class MoveMessageWizard(models.TransientModel):
    _name = 'move.message.wizard'
    _inherit = 'common.thread.wizard'

    thread_id = fields.Reference(
        string='Destination Mail Thread', size=128,
        selection=lambda self: get_model_selection(self), required=True)
    message_ids = fields.Many2many(
        'mail.message', 'message_move_rel', 'move_id', 'message_id',
        'Messages', readonly=True)
    leave_msg = fields.Boolean(
        'Preserve original messages',
        help="Check for no remove message from original thread.", default=True)

    @api.guess
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if uid != SUPERUSER_ID and not self.pool['res.users'].has_group(
                cr, uid, 'xopgi_mail_move_message.group_move_message'):
            raise AccessError(_('Access denied.'))
        result = super(MoveMessageWizard, self).fields_view_get(
            cr, uid,
            view_id=view_id,
            view_type=view_type,
            context=context,
            toolbar=toolbar,
            submenu=submenu
        )
        return result

    @api.onchange('thread_id')
    @api.depends('thread_id')
    def onchange_thread_id(self):
        if self.thread_id:
            self.model_id = self.thread_id._name

    @api.model
    def default_get(self, fields_list):
        values = super(MoveMessageWizard, self).default_get(fields_list)
        if 'message_ids' in fields_list:
            values['message_ids'] = self._context.get('active_ids', [])
        return values

    @api.multi
    def confirm(self):
        '''Create a new mail thread, remove original message if not
        leave_msg  and open new thread on edit form.

        '''
        self.message_ids.do_move_message(
            self.thread_id._name, self.thread_id.id, self.leave_msg
        )
        try:
            # Can I read the thread model?  If not, the message it's there but
            # I cannot be redirected to the model's view.
            self.thread_id.read([])
        except AccessError:
            return RELOAD_UI
        else:
            return self.get_thread_action(res_id=self.thread_id.id)
