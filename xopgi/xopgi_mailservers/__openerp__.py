#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name="Same server policy",
    version="1.4",
    author="Merchise Autrement",
    category="Hidden",
    depends=["xopgi_mail_threads"],
    description='Send emails via the right SMTP server. ',
    data=[
        'views/%d/server.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    auto_install=False,
)
