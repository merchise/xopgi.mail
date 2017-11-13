#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, fields, models
from xoeuf.odoo import exceptions, SUPERUSER_ID, _
from xoeuf.odoo.addons.xopgi_mail_threads.mail_messages import RAW_EMAIL_ATTR

from xoeuf import signals

FIELDS2READ = ['type', 'message_id', 'subject', 'email_from', 'date',
               'author_id', 'parent_id', 'body', 'attachment_ids',
               RAW_EMAIL_ATTR]


class NewThreadWizard(models.TransientModel):
    _name = 'new.thread.wizard'
    _inherit = 'common.thread.wizard'

    message_id = fields.Many2one('mail.message', 'Message', readonly=True)
    leave_msg = fields.Boolean(
        'Preserve original message', default=True,
        help="Check for no remove message from original thread.")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        context = dict(self._context or {})
        if self._uid != SUPERUSER_ID and not self.env['res.users'].has_group(
                'xopgi_mail_new_thread.group_new_thread'):
            raise exceptions.AccessDenied()
        if view_type == 'form':
            if (len(context.get('active_ids', [])) > 1 or not context.get(
                    'default_message_id', False)):
                raise exceptions.ValidationError(
                    _('You should select one and only one message.')
                )
        result = super(NewThreadWizard, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        return result

    @api.multi
    def confirm(self):
        '''Create a new mail thread, post new message, remove original
        message if not leave_msg and open new thread on edit form.

        '''
        thread_model = self.env[self.model_id]
        self.ensure_one()
        context = dict(
            wizard_id=self.id,
            new_thread_from_mail_msg=True,
            thread_model=self.model_id
        )
        rec_name = thread_model.fields_get().get(
            thread_model._rec_name or 'name',
            False
        )
        if rec_name and rec_name['type'] in ('char', 'text'):
            name = self.message_id.subject or self.message_id.display_name
            if name:
                context['default_%s' % (thread_model._rec_name or 'name')] = name
        return self.with_context(**context).get_thread_action()


@signals.receiver(signals.post_create)
def move_message(self, signal, result, values):
    """If a mail thread is created from an active new.thread.wizard the
    selected message is moved/copied and the new.thread.wizard is deleted.

    """
    if self._context.get('new_thread_from_mail_msg', False) and \
            self._name == self._context.get('thread_model', ''):
        if self._context.get('wizard_id', False):
            wizard = self.env['new.thread.wizard'].search(
                [('id', '=', self._context['wizard_id'])]
            )
        else:
            wizard = False
        if wizard:
            wizard.message_id.do_move_message(
                self._name,
                result.id,
                wizard.leave_msg
            )
            wizard.unlink()
