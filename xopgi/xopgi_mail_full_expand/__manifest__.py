#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'XOPGI Mail Full Expand',
    'version': '2.0',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': 8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    'summary': 'Add an option to open the mail in a big window.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads'
    ],
    'description': 'Allows you to expand a message in a new window',
    'data': [
        'views/%d/mail_full_expand_view.xml' % MAJOR_ODOO_VERSION,  # noqa
        'views/%d/assets.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_full_expand.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
}
