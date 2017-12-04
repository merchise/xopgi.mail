#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name="Merchise Autrement's Email Templates",
    version='1.4',
    author='Merchise Autrement',
    category='Mail',
    depends=['email_template' if MAJOR_ODOO_VERSION < 9 else 'mail'],  # noqa
    data=[
        'views/%d/mail_compose_message_view.xml' % MAJOR_ODOO_VERSION,  # noqa
        'views/%d/email_template_view.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    demo=[],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa
    auto_install=True,
)
