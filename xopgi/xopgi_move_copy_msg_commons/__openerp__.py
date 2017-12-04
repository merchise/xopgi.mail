#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'Move Message commons',
    'version': '1.0',
    "author": 'Merchise Autrement',
    'category': 'Internal',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    'summary': 'Add method to move messages.',
    'depends': [
        'mail',
        'xopgi_mail_threads',
    ],
    'data': [
        'views/%d/config.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
}
