#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='Avoid replying from the wall',
    depends=['mail', ],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    application=False,
    category='Mail',
    summary=('Disallows replying from the wall, effectively disallowing '
             'replying to direct emails before converting them to '
             'proper object'),
    data=[
        'views/%d/assets.xml' % MAJOR_ODOO_VERSION,   # noqa
    ]
)
