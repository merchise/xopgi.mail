#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
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


from openerp.osv.orm import Model
from openerp.osv import fields


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

        'module_xopgi_mail_verp': fields.boolean(
            'Add VERP mail management.'),

        'module_xopgi_mail_new_thread':
            fields.boolean('Add new mail thread management.'),
    }
