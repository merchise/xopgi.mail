# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-04-11

dict(
    name="Merchise Autrement's Email Templates",
    version='1.4',
    author='Merchise Autrement',
    category='Mail',
    depends=['email_template'],
    data=[
        'views/mail_compose_message_view.xml',
        'views/email_template_view.xml'
    ],
    demo=[],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    auto_install=True,
)
