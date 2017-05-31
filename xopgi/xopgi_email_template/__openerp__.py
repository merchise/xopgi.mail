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
    depends=['email_template' if ODOO_VERSION_INFO < (9, 0) else 'mail'],  # noqa
    data=[
        'views/%d/mail_compose_message_view.xml' % ODOO_VERSION_INFO[0],  # noqa
        'views/%d/email_template_view.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
    demo=[],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO[0] < (11, 0),   # noqa
    auto_install=True,
)
