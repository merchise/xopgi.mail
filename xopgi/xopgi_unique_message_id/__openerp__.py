#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_unique_message_id',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    summary='Mail Hotfix.',
    description=('Avoid Duplicated Message Id on db.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[
        'data/%d/message_sequence.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
)
