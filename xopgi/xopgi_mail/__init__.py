#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Mail related addons.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import fields, models


class MailConfig(models.TransientModel):
    _name = _inherit = 'base.config.settings'

    module_xopgi_mail_full_expand = fields.Boolean(
        'Allow to "expand" messages.'
    )

    module_xopgi_mail_forward = fields.Boolean(
        'Allow to "forward" messages.'
    )

    module_xopgi_mailservers = fields.Boolean(
        'Control outgoing SMTP server by sender.'
    )

    module_xopgi_mail_alias_crm = fields.Boolean(
        'Allow several mail alias by sale team.'
    )

    module_xopgi_mail_alias_project = fields.Boolean(
        'Allow several mail alias by project.'
    )

    module_xopgi_mail_verp = fields.Boolean(
        'Notify (if possible) authors about message bounces (VERP).'
    )

    module_xopgi_mail_new_thread = fields.Boolean(
        'Allow to create an new object from an existing message.'
    )

    module_xopgi_mail_move_message = fields.Boolean(
        'Allow to transfer messages.'
    )

    module_xopgi_thread_address = fields.Boolean(
        'Generate a unique email address per thread.'
    )

    module_xopgi_unique_message_id = fields.Boolean(
        'Generate a unique id per message on DB.'
    )

    module_xopgi_mail_url_attachments = fields.Boolean(
        'Add URL attachments from links on messages body.'
    )

    module_xopgi_mail_disclosure = fields.Boolean(
        'Disclose recipients in outgoing emails.'
    )

    module_xopgi_mail_alias = fields.Boolean(
        'Check aliases domains when receiving messages'
    )

    module_xopgi_mail_nowall = fields.Boolean(
        'Disallow replying from the Message Wall.'
    )

    module_xopgi_mail_expose_recipients = fields.Boolean(
        'Expose original recipients of incoming messages.'
    )
