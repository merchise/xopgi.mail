# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_bounce_model
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

'''A transient model to avoid send notification mails on bounced messages.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil import Unset
from xoutil import logger as _logger

from openerp import tools
from openerp.osv import orm
from openerp.tools.translate import _

from .common import BOUNCE_MODEL, VOID_EMAIL_ADDRESS


class MailBounce(orm.TransientModel):
    _name = BOUNCE_MODEL

    def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        '''Log an exception to see if this case happen.

        This is not expected to happen cause a bounce should never start a new
        thread.

        '''
        _logger.error(
            "Bounced mail '%s' to <%s> receive with non thread_id",
            msg_dict.get('message_id'),
            msg_dict.get('to'),
        )
        return False

    def message_update(self, cr, uid, ids, msg_dict, update_vals=None,
                       context=None):
        # Conceptually this is not needed, cause its purpose is to update the
        # object record from an email data.  Being a bounce we mustn't modify
        # any record for that sort of thing.  However, this is method is still
        # needed to keep Odoo from calling `message_new`.
        return True

    def message_post(self, cr, uid, ids, **kwargs):
        '''Post the bounce to the proper thread.

        Change the email_from with the email_to of the original message (not
        the bounce) and add "mail_notify_noemail" magic key to the context
        before actually posting the message to avoid sending notification
        mails.

        .. note:: The `ids` is expected to be a single item with a tuple with
           ``(message_id, model, thread_id, failed_recipient, raw_message)``,
           being the `message_id` the id of the message that bounced, `model`
           the model to which the message belongs, `thread_id` of the object
           (from model) that identifies the thread, `failed_recipient` the
           email address that bounced, and `raw_message` the bounce message.

        '''
        message_id, model, thread_id, recipient, rfc_message = ids[0]
        if not model:
            return
        context = kwargs.setdefault('context', {})
        model_pool = self.pool[model]
        if not hasattr(model_pool, 'message_post'):
            context['thread_model'] = model
            model_pool = self.pool['mail.thread']
        if thread_id:
            # TODO: Prove this happens by inspecting the log.
            # thread_id must time will be an integer but on a few cases can be
            # a str (virtual id) e.g. recurrent events
            try:
                thread_id = int(thread_id)
            except ValueError:
                _logger.warn('Invalid thread while bounce %s', thread_id)
        message = self._get_message(cr, uid, int(message_id))
        self._build_bounce(cr, uid, rfc_message, message, recipient, kwargs)
        if message.author_id and any(message.author_id.user_ids):
            # Notify to the author of the original email IF AND ONLY IF it
            # is a 'res_user'. This is to avoid notifying third parties about
            # recipients they probably don't know about.
            partner_ids = [message.author_id.id]
        else:
            partner_ids = []
        context.update(
            thread_model=model,
            partner_ids=partner_ids,
            forced_followers=partner_ids,
            # Don't make the superuser a follower
            mail_post_autofollow=False,
        )
        msgid = model_pool.message_post(cr, uid, [thread_id], **kwargs)
        return msgid

    def _build_bounce(self, cr, uid, rfc_message, message, recipient, params):
        '''Rewrites the bounce email.
        '''
        params['subject'] = rfc_message['subject'] or _('Mail Returned to Sender')
        params['type'] = 'notification'
        params['email_from'] = VOID_EMAIL_ADDRESS
        context = params.setdefault('context', {})
        context['auto_submitted'] = 'auto-replied'
        part = find_part(rfc_message)
        if part:
            encoding = part.get_content_charset()  # None if attachment
            params['body'] = tools.append_content_to_html(
                '',
                tools.ustr(part.get_payload(decode=True),
                           encoding, errors='replace'),
                preserve=True
            )
        return params

    def _get_message(self, cr, uid, message_id):
        return self.pool['mail.message'].browse(cr, uid, message_id)


class mail_notification(orm.Model):
    _inherit = 'mail.notification'

    def update_message_notification(self, cr, uid, ids, message_id,
                                    partner_ids, context=None):
        # If the forced_followers is set, override the partner_ids.
        context = dict(context or {})
        forced_followers = context.pop('forced_followers', Unset)
        if forced_followers is not Unset:
            partner_ids = forced_followers
        return super(mail_notification, self).update_message_notification(
            cr, uid, ids, message_id, partner_ids, context=context
        )


class mail_mail(orm.Model):
    _inherit = 'mail.mail'

    def create(self, cr, uid, values, context=None):
        from six import string_types
        if context:
            auto_submitted = context.get('auto_submitted')
        else:
            auto_submitted = None
        if auto_submitted:
            headers = values.get('headers', {})
            if isinstance(headers, string_types):
                headers = eval(headers)
            headers['Auto-Submitted'] = auto_submitted
            values['headers'] = str(headers)
        return super(mail_mail, self).create(cr, uid, values, context=context)


def find_part(msg, type='text/plain'):
    from email.message import Message
    if msg.get_content_type() == type:
        return msg
    if msg.is_multipart:
        for part in msg.get_payload():
            if not isinstance(part, Message):
                continue
            ret = find_part(part)
            if ret:
                return ret
    return None
