#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'xopgi_mail_alias_crm',
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'mail',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # WARNING: Although we allow this addon to be installed in Odoo 9 it does
    # not do much.  It's only allowed to ease the migration from Odoo 8 to
    # Odoo 10.
    'installable': MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    'summary': 'Mail Alias CRM (sales_team).',
    'description': 'Extend crm module to relate many alias per sale team.',
    'depends': ['crm', 'xopgi_mail_alias'],

    'data': [
        'view/%d/crm_view.xml' % MAJOR_ODOO_VERSION,  # noqa
        'security/%d/security.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
}
