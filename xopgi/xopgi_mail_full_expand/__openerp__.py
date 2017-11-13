#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
# flake8: noqa

{
    'name': 'XOPGI Mail Full Expand',
    'version': '2.0',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (11, 0),   # noqa

    'summary': 'Add an option to open the mail in a big window.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads'
    ],
    'description': 'This add-ons allows you to expand a message in a new window as a master detail',
    'data': [
        'views/%d/mail_full_expand_view.xml' % ODOO_VERSION_INFO[0],
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],
    ],
    'qweb': [
        'static/src/xml/%d/mail_full_expand.xml' % ODOO_VERSION_INFO[0],
    ],
}
