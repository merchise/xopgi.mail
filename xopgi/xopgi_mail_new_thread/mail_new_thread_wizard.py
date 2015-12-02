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
from openerp.exceptions import AccessError
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.addons.xopgi_mail_threads.mail_messages import RAW_EMAIL_ATTR

FIELDS2READ = ['type', 'message_id', 'subject', 'email_from', 'date',
               'author_id', 'parent_id', 'body', 'attachment_ids',
               RAW_EMAIL_ATTR]


class NewThreadWizard(osv.TransientModel):
    _name = 'new.thread.wizard'

    def _get_model_selection(self, cr, uid, context=None):
        """Get message_capable_models where uid can write and create.

        """
        thread_obj = self.pool['mail.thread']
        check = lambda model, operation: (
            self.pool[model].check_access_rights(cr, uid, operation,
                                                 raise_exception=False))
        translate = lambda source: (
            self.pool['ir.translation']._get_source(
                cr, SUPERUSER_ID, None, ('model',),
                (context or {}).get('lang', False), source) or source)
        models = [(n, translate(d))
                  for n, d in thread_obj.message_capable_models(
                      cr, uid, context=context).items()
                  if (n != 'mail.thread'
                      and hasattr(self.pool[n], 'message_new')
                      and check(n, 'create') and check(n, 'write'))]
        return models

    _columns = {
        'model_id':
            fields.selection(_get_model_selection, 'Model', required=True),
        'message_id':
            fields.many2one('mail.message', 'Message', readonly=True),
        'leave_msg':
            fields.boolean('Preserve original message',
                           help="Check for no remove message from original "
                                "thread."),
    }

    _defaults = {
        'leave_msg': True
    }

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

    def confirm(self, cr, uid, ids, context=None):
        '''Create a new mail thread, post new message, remove original
        message if not leave_msg and open new thread on edit form.

        '''
        wiz = self.browse(cr, uid, ids[0], context=context)
        msg_obj = self.pool['mail.message']
        msg_dict = {key: value
                    for key, value in msg_obj.read(
                        cr, uid, wiz.message_id.id, FIELDS2READ,
                        context=context).iteritems()
                    if value}
        #  Some models expect from and cc keys.
        #  e.g. crm.lead, project.issue, ...
        msg_dict['from'] = msg_dict.get('email_from') if msg_dict else False
        msg_dict['cc'] = msg_dict.get('email_cc') if msg_dict else False
        #  Extract id from id, name tuple on author_id and parent_id values.
        if msg_dict and isinstance(msg_dict.get('author_id', False), tuple):
            msg_dict['author_id'] = msg_dict['author_id'][0]
        # When new thread is created, parent is irrelevant
        msg_dict.pop('parent_id', None)
        custom_values = {}
        if not msg_dict.get('subject', False):
            custom_values['name'] = _(
                'Create from a mail message without subject.')
        thread_obj = self.pool[wiz.model_id]
        thread_id = thread_obj.message_new(cr, SUPERUSER_ID, msg_dict,
                                           custom_values=custom_values,
                                           context=context)
        thread_obj.message_post(cr, SUPERUSER_ID, [thread_id], context=context,
                                subtype='mail.mt_comment', **msg_dict)
        if not wiz.leave_msg:
            msg_obj.unlink(cr, SUPERUSER_ID, wiz.message_id.id, context=context)
        try:
            thread_obj.read(cr, uid, thread_id, [], context=context)
            return {
                'name': _('New Document from Mail Message'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wiz.model_id,
                'res_id': thread_id,
                'type': 'ir.actions.act_window',
                'context': dict(context or {}, active_id=thread_id)
            }
        except AccessError:
            return {'type': 'ir.actions.client', 'tag': 'reload', }
