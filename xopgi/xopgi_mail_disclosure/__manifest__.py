#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_mail_disclosure',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    summary='Disclose notified partners in notifications',
    description=('Appends a Cc disclosing notified partners in outgoing '
                 'emails.'),
    depends=['mail', ],
)
