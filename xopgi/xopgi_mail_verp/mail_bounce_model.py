#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''A transient model to avoid send notification mails on bounced messages.

'''
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.symbols import Unset

from xoeuf import api, models
from xoeuf.odoo import tools, _

from .common import (
    BOUNCE_MODEL,
    AUTOMATIC_RESPONSE_MODEL,
    VOID_EMAIL_ADDRESS,
)


import logging
_logger = logging.getLogger(__name__)
del logging


class BounceVirtualId(object):
    '''An object that represents a virtual id for bounces.

    The ids of `MailBounce` objects are expected to be instances of this type.

    '''
    def __init__(self, message_id, model, thread_id, recipient, message):
        self.message_id = message_id
        self.model = model
        self.thread_id = thread_id
        self.recipient = recipient
        self.message = message

    @property
    def args(self):
        return (self.message_id, self.model, self.thread_id,
                self.recipient, self.message)

    def __iter__(self):
        # Odoo 9
        return iter([self, ])


class MailAutomaticResponse(models.TransientModel):
    _name = AUTOMATIC_RESPONSE_MODEL

    @api.multi
    def message_new(self, msg_dict, custom_values=None):
        '''Log an exception to see if this case happen.

        This is not expected to happen cause an automatic response should never
        start a new thread.

        '''
        _logger.error(
            "Bounced mail '%s' to <%s> receive with non thread_id",
            msg_dict.get('message_id'),
            msg_dict.get('to'),
        )
        return False

    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        # Conceptually this is not needed, cause its purpose is to update the
        # object record from an email data.  Being an automatic response we
        # mustn't modify any record for that sort of thing.  However, this
        # method is still needed to keep Odoo from calling `message_new`.
        return True

    @api.multi
    def message_post(self, **kwargs):
        '''Post the automatic response to the proper thread.

        Change the email_from and add "mail_notify_noemail" magic key to the
        context before actually posting the message to avoid sending
        notification mails.

        `ids` must a sequence with a single BounceVirtualId instance.

        '''
        data = self._ids[0]
        message_id, model, thread_id, recipient, rfc_message = data.args
        if not model:
            return
        context = dict(self._context)
        model_pool = self.env[model]
        if not hasattr(model_pool, 'message_post'):
            context['thread_model'] = model
            model_pool = self.env['mail.thread']
        if thread_id:
            # TODO: Prove this happens by inspecting the log.
            # thread_id must time will be an integer but on a few cases can be
            # a str (virtual id) e.g. recurrent events
            try:
                thread_id = int(thread_id)
            except ValueError:
                _logger.warn('Invalid thread while bounce %s', thread_id)
        if message_id:
            message = self.env['mail.message'].browse(int(message_id))
        else:
            # This means we recognized this message as 'rogue bounce' which
            # could not find the message that bounced.
            message = None
        # Rewrite params of outgoing notification
        kwargs['message_type'] = 'notification'
        kwargs['email_from'] = VOID_EMAIL_ADDRESS
        if message and message.author_id and any(message.author_id.user_ids):
            # Notify to the author of the original email IF AND ONLY IF it
            # is a 'res_user'. This is to avoid notifying third parties about
            # recipients they probably don't know about.
            partner_ids = [message.author_id.id]
        else:
            # TODO:  Notify internal users.
            partner_ids = []
        context.update(
            thread_model=model,
            partner_ids=partner_ids,
            forced_followers=partner_ids,
            # Don't make the superuser a follower
            mail_post_autofollow=False,
            auto_submitted=rfc_message.get('Auto-Submitted', ''),
            content_type=rfc_message.get('Content-Type', '')
        )
        return model_pool.browse(thread_id).with_context(context).message_post(**kwargs)


class MailBounce(MailAutomaticResponse, models.TransientModel):
    _name = BOUNCE_MODEL

    @api.multi
    def message_post(self, **kwargs):
        '''Post the bounce to the proper thread.

        Format bounce notification before posting.

        '''

        data = self._ids[0]
        message_id, model, thread_id, recipient, rfc_message = data.args
        if message_id:
            message = self.env['mail.message'].browse(int(message_id))
        else:
            message = None
        self._build_bounce(rfc_message, message, recipient, kwargs)
        return super(MailBounce, self).message_post(**kwargs)

    def _build_bounce(self, rfc_message, message, recipient, params):
        '''Rewrites the bounce email.
        '''
        subject = rfc_message['subject']
        if subject:
            params['subject'] = subject + _(' -- Detected as bounce')
        else:
            params['subject'] = _('Mail Returned to Sender')
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


class MessageBounceNotification(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def _notify(self, *args, **kwargs):
        forced_followers = self.env.context.get('forced_followers', Unset)
        if forced_followers is not Unset and self.model:
            thread = self.env[self.model].browse(self.res_id).sudo()
            followers = thread.message_follower_ids.mapped(lambda f: f.partner_id)
            channels = thread.message_channel_ids.mapped('id')
            thread.message_unsubscribe(followers.mapped('id'), channels)
            thread.message_subscribe(forced_followers)
        else:
            thread = None
            followers = None
        try:
            return super(MessageBounceNotification, self)._notify(
                *args, **kwargs
            )
        finally:
            if followers and thread:
                thread.message_subscribe(followers.mapped('id'), channels)


class Mail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        # Keep track of automatic responses in outgoing messages.
        # This way the possibility of mail loops is reduced.
        from xoutil.eight import string_types
        content_type = self._context.get('content_type')
        auto_submitted = self._context.get('auto_submitted')
        headers = values.get('headers', {})
        if isinstance(headers, string_types):
            headers = eval(headers)
            if self._is_not_empty(content_type):
                headers['Content-type'] = content_type
            if self._is_not_empty(auto_submitted):
                headers['Auto-Submitted'] = auto_submitted
        values['headers'] = str(headers)
        return super(Mail, self).create(values)

    @classmethod
    def _is_not_empty(cls, content):
        return bool(content and content.strip())


def find_part(msg, type='text/plain'):
    from email.message import Message
    if msg.get_content_type() == type:
        return msg
    if msg.is_multipart:
        for part in msg.get_payload():
            if not isinstance(part, Message):
                continue   # noqa
            ret = find_part(part)
            if ret:
                return ret
    return None
