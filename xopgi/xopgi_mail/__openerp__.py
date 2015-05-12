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
    'name': 'Mail Extensions',
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,
    'installable': True,
    'summary': 'Several extensions to OpenERP Messaging System',
    'depends': ['mail', 'web'],
    'data': [
        'views/config.xml',
    ],
    'description': '',
    'auto_install': True,
}
