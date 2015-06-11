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
from openerp import SUPERUSER_ID


class NewThreadWizard(osv.TransientModel):
    _name = 'new.thread.wizard'

    def _get_model_selection(self, cr, uid, context=None):
        """Get message_capable_models where uid can write and create.

        """
        thread_obj = self.pool['mail.thread']
        check = lambda model, operation: (
            self.pool[model].check_access_rights(cr, uid, operation,
                                                 raise_exception=False))
        models = [(n, d)
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

    def confirm(self, cr, uid, ids, context=None):
        '''Create a new mail thread, post new message, remove original
        message if not leave_msg and open new thread on edit form.

        '''
        wiz = self.browse(cr, uid, ids[0], context=context)
        msg_obj = self.pool['mail.message']
        msg_dict = msg_obj.read(cr, uid, wiz.message_id.id,
                                ['type', 'message_id', 'subject',
                                 'email_from', 'date', 'author_id',
                                 'parent_id', 'body', 'attachment_ids'],
                                context=context)
        msg_dict['from'] = msg_dict.get('email_from') if msg_dict else False
        if msg_dict and isinstance(msg_dict.get('author_id', False), tuple):
            msg_dict['author_id'] = msg_dict['author_id'][0]
        if msg_dict and isinstance(msg_dict.get('parent_id', False), tuple):
            msg_dict['parent_id'] = msg_dict['parent_id'][0]
        thread_obj = self.pool[wiz.model_id]
        thread_id = thread_obj.message_new(cr, uid, msg_dict, {},
                                           context=context)
        thread_obj.message_post(cr, uid, [thread_id], context=context,
                                subtype='mail.mt_comment', **msg_dict)
        if not wiz.leave_msg:
            msg_obj.unlink(cr, SUPERUSER_ID, wiz.message_id.id, context=context)
        return {
            'name': _('New Document from Mail Message'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wiz.model_id,
            'res_id': thread_id,
            'type': 'ir.actions.act_window',
            'context': dict(context or {}, active_id=thread_id)
        }
