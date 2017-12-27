#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'XOPGI Mail Filters',
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,
    'summary': 'Add default filters for messages.',
    'depends': ['base', 'mail'],
    'data': [
        'views/config.xml',
        'views/mail_message_search.xml',
        'views/search.xml'
    ],
    'auto_install': True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.  Although this addon is installable in Odoo 9, it's
    # only so to make easier the migration from Odoo 8 to 10.
    'installable': 8 <= MAJOR_ODOO_VERSION < 11,   # noqa
}
