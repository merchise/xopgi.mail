#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    # Internal addon, it should be auto-installed when both no-wall and
    # forward are installed.
    depends=['xopgi_mail_nowall', 'xopgi_mail_forward'],
    name='xopgi_mail_nowall_forward',
    summary='Makes the no-replying from wall be activated for forwarding',
    description='Makes the no-replying from wall be activated for forwarding',
    application=False,

    data=[
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],   # noqa
    ],

    auto_install=True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # Note: This addon will not be used in Odoo 10 because in the Inbox the
    # 'Reply with copy' functionality will not be displayed. Instead, the
    # 'Reply' functionality will be used.
    installable=(8, 0) <= ODOO_VERSION_INFO < (10, 0),   # noqa

)
