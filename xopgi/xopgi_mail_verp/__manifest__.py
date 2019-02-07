#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_mail_verp',
    version='3.1',
    author='Merchise Autrement',
    category='Hidden',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them:  Supported versions 8 and 10.
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    summary='Variable Envelop Return Path (VERP)',
    description=('Allows to track email bounces and add them to the '
                 'proper thread.'),
    depends=[
        'mail',
        'xopgi_mail_threads',

        # The rogue bounce detector for Aguas de la Habana assumes the
        # outgoing messages are being delivered through this Transport.
        'xopgi_thread_address',
    ],
    external_dependencies={'python': ['flufl.bounce']},
    data=[
        'data/init.xml',

        'data/cron.xml',
        'data/acl.xml',
    ],
)
