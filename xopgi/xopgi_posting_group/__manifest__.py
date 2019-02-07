#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi.posting_group',
    summary='Allow to enable/disable auto-subscription in groups',

    author='Merchise Autrement',
    category='Hidden',
    version='1.0',
    depends=['mail', ],
    data=[
        'views/mail_group_view.xml',
    ],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # Note: mail.group disappear since in Odoo 9. Instead the channel it's
    # brought to live. As channels behave like we need, we keep them
    # untouched.
    installable=8 <= MAJOR_ODOO_VERSION < 9,   # noqa
)
