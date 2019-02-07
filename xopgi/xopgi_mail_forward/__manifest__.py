#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'XOPGI Mail Forward',
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': 8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    'summary': 'Allow to forward messages including the text of the original',
    'depends': ['mail', 'web'],
    'description': 'In any conversation thread that includes messaging Allow'
                    'to forward messages including the text of the original',
    'data': [
        'views/mail_forward_wizard.xml',
        'views/%d/assets.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_forward.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
}
