#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Eddy Ernesto del Valle Pino <eddy@merchise.org>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


{
    'name': 'Desabilitate Share Followers',
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'summary': '',
    'description': '',
    'depends': ['mail', 'web'],
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
