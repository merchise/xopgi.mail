# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_bounce_model
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

'''
A transiend model to avoid send notification mails on bounced messages.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from openerp.osv import orm
from xoutil import logger as _logger


class mail_bounce_model(orm.TransientModel):
    _name = 'mail.bounce.model'

    def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        '''
        Log an exception to see if this case happen.
        '''
        _logger.exception(
            "Bounced mail '%s' to <%s> receive with non thread_id",
            msg_dict.get('message_id'),
            msg_dict.get('to'),
        )
        return False

    def message_update(self, cr, uid, ids, msg_dict, update_vals=None, context=None):
        '''
        Redirect to the origin model correspondent method.
        '''
        mail_id, model, thread_id = ids[0]  # assumed are only one
        ctx = dict(
            context or {},
            thread_model=model
        )
        model_pool = self.pool[model]
        if hasattr(model_pool, 'message_update'):
            model_pool.message_update(cr, uid, [int(thread_id)], msg_dict,
                                      context=ctx)
        else:
            nosub_ctx = dict(ctx, mail_create_nolog=True)
            model_pool.message_new(cr, uid, msg_dict, {}, context=nosub_ctx)
            _logger.warn(
                "Bounced mail '%s' to <%s> own to a model '%s' without "
                "message_update method.",
                msg_dict.get('message_id'), msg_dict.get('to'), model
            )
        return True

    def message_post(self, cr, uid, ids, **kwargs):
        '''
        Change the email_from by the email_to of original message and Add
        "mail_notify_noemail" magic key on context before call the
        message post os the real bounced model to avoid send notification
        mails.
        '''
        # Add context entries.
        mail_id, model, thread_id = ids[0]  # assumed are only one
        context = dict(
            kwargs.get('context', {}) or {},
            mail_notify_noemail=True,
            thread_model=model
        )
        kwargs.update(context=context)
        # Update email_from header.
        mail_pool = self.pool['mail.mail']
        mail_id = mail_pool.exists(cr, uid, [int(mail_id)], context=context)
        if mail_id:
            mail = mail_pool.browse(cr, uid, mail_id[0], context=context)
            if mail.email_to:
                kwargs.update(email_from=mail.email_to)
        # call model message_post method.
        model_pool = self.pool[model]
        if not hasattr(model_pool, 'message_post'):
            context['thread_model'] = model
            model_pool = self.pool['mail.thread']
        return model_pool.message_post(cr, uid, [thread_id], **kwargs)