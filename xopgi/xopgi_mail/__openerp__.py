#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
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
    'description': 'Provides a configurable interface to Messaging Extensions',
    'depends': ['mail', 'web'],
    'data': [
        'views/config.xml',
    ],
    'auto_install': True,
    'installable': (8, 0) <= ODOO_VERSION_INFO < (10, 0),  # noqa
}
