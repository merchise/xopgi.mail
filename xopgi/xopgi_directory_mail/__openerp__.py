# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_directory_mail.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-09-30


dict(
    name='xopgi_directory_mail',
    version='1.0',
    author='Merchise Autrement',
    category='Hidden',
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    auto_install=True,
    summary='Integrate the directory with mail.',
    depends=['mail', 'xopgi_directory'],
    data=['views/mail_compose_message_view.xml'],
)
