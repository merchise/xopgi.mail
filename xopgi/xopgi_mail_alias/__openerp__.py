#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_mail_alias',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # WARNING: Although we allow this addon to be installed in Odoo 9 it does
    # not do much.  It's only allowed to ease the migration from Odoo 8 to
    # Odoo 10.
    installable=MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    summary='Mail Alias Extension.',
    description=('Allow to user edit alias domain and check for it '
                 'on income message routing.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[],
)
