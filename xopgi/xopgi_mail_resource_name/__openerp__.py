#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'XOPGI Mail Show Resource Name',
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': 8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    'auto_install': True,
    'summary': 'Show resource name.',
    'depends': ['mail'],
    'description': 'Show resource name of a mail.',
    'data': [
        'views/%d/resource_name_view.xml' % MAJOR_ODOO_VERSION,   # noqa
    ],
}
