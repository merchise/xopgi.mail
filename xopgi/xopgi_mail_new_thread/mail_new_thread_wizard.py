# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
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
from openerp.addons.xopgi_mail_threads.mail_messages import RAW_EMAIL_ATTR
from openerp.addons.xopgi_move_copy_msg_commons import get_model_selection
from xoeuf import signals

FIELDS2READ = ['type', 'message_id', 'subject', 'email_from', 'date',
               'author_id', 'parent_id', 'body', 'attachment_ids',
               RAW_EMAIL_ATTR]


class NewThreadWizard(models.TransientModel):
    _name = 'new.thread.wizard'

    model_id = fields.Selection(
        lambda self: get_model_selection(self), 'Model', required=True)
    message_id = fields.Many2one('mail.message', 'Message', readonly=True)
    leave_msg = fields.Boolean(
        'Preserve original message', default=True,
        help="Check for no remove message from original thread.")

    @api.guess
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        context = dict(context or {})
        if uid != SUPERUSER_ID and not self.pool['res.users'].has_group(
                cr, uid, 'xopgi_mail_new_thread.group_new_thread'):
            raise osv.except_osv(_('Error!'), _('Access denied.'))
        if view_type == 'form':
            if (len(context.get('active_ids', [])) > 1
                    or not context.get('default_message_id', False)):
                raise osv.except_osv(_('Error!'), _(
                    'You should select one and only one message.'))
        result = super(NewThreadWizard, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        return result

    @api.multi
    def confirm(self):
        '''Create a new mail thread, post new message, remove original
        message if not leave_msg and open new thread on edit form.

        '''
        return {
            'name': _('New Document from Mail Message'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.model_id,
            'type': 'ir.actions.act_window',
            'context': dict(self._context,
                            new_thread_from_mail_msg=True,
                            message_id=self.message_id.id,
                            leave_msg=self.leave_msg)
        }


@signals.receiver(signals.post_create)
def move_message(self, signal, result, values):
    if self._context.get('new_thread_from_mail_msg', False) and \
            self._name in self.env['mail.thread'].message_capable_models():
        message = self.env['mail.message'].browse(
            self._context.get('message_id', False))
        message.do_move_message(self._name, result.id,
            self._context.get('leave_msg', True))
