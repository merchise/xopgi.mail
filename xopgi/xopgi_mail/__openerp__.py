#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


dict(
    name='Mail Extensions',
    version='1.4',
    author='Merchise Autrement',
    category='Hidden',
    application=False,
    summary='Several extensions to OpenERP Messaging System',
    description='Provides a configurable interface to Messaging Extensions',
    depends=['mail', 'web'],
    data=[
        'views/%d/config.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    auto_install=True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=8 <= MAJOR_ODOO_VERSION < 12,  # noqa
)
