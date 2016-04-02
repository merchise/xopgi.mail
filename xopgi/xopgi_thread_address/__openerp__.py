#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_thread_address
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-06-03

dict(
    name='xopgi_thread_address',
    version='1.4',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    summary='Unique thread address',
    description=('Ensure each mail thread has a unique address to respond '
                 'to.  You must ensure your MTA accepts dynamic addresses.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[],
)
