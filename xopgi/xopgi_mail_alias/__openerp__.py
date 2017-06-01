#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_alias.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# Author: Merchise Autrement [~º/~]
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


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
    installable=ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    summary='Mail Alias Extension.',
    description=('Allow to user edit alias domain and check for it '
                 'on income message routing.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[],
)
