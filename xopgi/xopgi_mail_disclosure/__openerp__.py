#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-01

dict(
    name='xopgi_mail_disclosure',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=((8, 0) <= ODOO_VERSION_INFO < (9, 0)),   # noqa

    summary='Disclose notified partners in notifications',
    description=('Appends a Cc disclosing notified partners in outgoing '
                 'emails.'),
    depends=['mail', ],
)
