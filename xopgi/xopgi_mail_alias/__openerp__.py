#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_alias.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Merchise Autrement
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


dict(
    name='xopgi_mail_alias',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,
    installable=True,
    auto_install=True,
    summary='Mail Alias Extension.',
    description=('Allow to user edit alis domain and check for it '
                 'on income message routing.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=[],
)
