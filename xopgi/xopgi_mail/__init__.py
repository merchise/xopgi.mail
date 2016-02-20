#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-23

'''Mail related addons.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil import logger as _logger

from openerp.osv.orm import Model
from openerp.osv import fields

from openerp.signals import receiver
from openerp.addons.mail.xopgi import unlink_thread


class MailConfig(Model):
    _inherit = 'base.config.settings'

    _columns = {
        'module_xopgi_mail_forward':
            fields.boolean('Allow to "forward" messages.'),

        'module_xopgi_mailservers':
            fields.boolean('Control outgoing SMTP server by sender.'),

        'module_xopgi_mail_alias_crm':
            fields.boolean('Several mail alias by sale team.'),

        'module_xopgi_mail_alias_project':
            fields.boolean('Several mail alias by project.'),

        'module_xopgi_mail_verp':
            fields.boolean('Notify (if possible) authors about message '
                           'bounces.'),

        'module_xopgi_mail_new_thread':
            fields.boolean('Allow to create an new object from an existing '
                           'message.'),

        'module_xopgi_mail_move_message':
            fields.boolean('Allow to transfer messages.'),

        'module_xopgi_thread_address': fields.boolean(
            'Generate a unique email address per thread.'),

        'module_xopgi_unique_message_id': fields.boolean(
            'Generate a unique id per message on db.'),

        'module_xopgi_mail_url_attachments': fields.boolean(
            'Add URL attachments from links on messages body.'),

        'module_xopgi_mail_disclosure':
            fields.boolean('Disclose recipients in outgoing emails.'),

        'module_xopgi_mail_alias':
            fields.boolean('Check aliases domains when receiving messages'),

        'module_xopgi_mail_nowall':
            fields.boolean('Disallow replying from the Message Wall.'),
    }


@receiver(unlink_thread)
def log_thread_removal(sender, signal, **kwargs):
    name_get = getattr(sender, 'name_get')
    if name_get:
        which = name_get()
    else:
        which = sender
    messages_deleted = [_message_trace(message)
                        for message in sender.message_ids]
    _logger.warn('Removing thread %s', which,
                 extra=dict(
                     messages_deleted=messages_deleted,
                     messages_deleted_count=len(messages_deleted),
                 ))


def _message_trace(message):
    from xoutil.string import safe_encode
    result = 'from={from_}, at={at}, id={id}'
    if message.email_from:
        from_ = safe_encode(message.email_from)
    elif message.author_id:
        from_ = safe_encode(message.author_id.email)
    else:
        from_ = '?'
    return result.format(from_=from_, at=message.create_date,
                         id=safe_encode(message.message_id))
