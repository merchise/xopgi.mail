#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_one_line_subject',
    version='1.0',
    author='Merchise Autrement',
    category='Hidden',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (11, 0),   # noqa

    summary='One line subjects',
    description='Ensure one line subjects on outgoing messages.',
    depends=['mail', 'xopgi_mail_threads'],

    # This is a kind of bug-avoiding addon.  So let it be auto-installed.
    auto_install=True,
)
