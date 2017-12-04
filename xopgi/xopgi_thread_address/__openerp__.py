#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_thread_address',
    version='2.0',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=8 < MAJOR_ODOO_VERSION < 11,   # noqa

    summary='Unique thread address',
    description=('Ensure each mail thread has a unique address to respond '
                 'to.  You must ensure your MTA accepts dynamic addresses.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[],
)
