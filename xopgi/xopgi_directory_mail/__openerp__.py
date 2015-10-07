# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_directory_mail.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
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
    category='mail',
    application=False,
    installable=True,
    auto_install=True,
    summary='Mail extensions for directory.',
    description='Get fake and real partners con mail management',
    depends=['mail', 'xopgi_directory'],
    data=['views/mail_compose_message_view.xml'],
)
