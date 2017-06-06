#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_verp.__openerp__
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
    name='xopgi_mail_verp',
    version='3.1',
    author='Merchise Autrement',
    category='Hidden',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them:  Supported versions 8 and 10.
    installable=(8, 0) <= ODOO_VERSION_INFO < (11, 0),   # noqa

    summary='Variable Envelop Return Path (VERP)',
    description=('Allows to track email bounces and add them to the '
                 'proper thread.'),
    depends=['mail', 'xopgi_mail_threads'],
    external_dependencies={'python': ['flufl.bounce']},
    data=[
        'data/init.xml',

        'data/cron.xml',
        'data/acl.xml',
    ],
)
