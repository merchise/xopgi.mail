#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.__openerp__
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
    'name': 'XOPGI Mail Filters',
    'version': '1.2',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,
    'installable': True,
    'summary': 'Add default filters for messages.',
    'depends': ['base', 'mail'],
    'data': [
        'data/extend_search_views.xml',
        'views/config.xml',
        'views/mail_message_search.xml',
        (
            'views/8/search.xml'
            if ODOO_VERSION_INFO >= (8, )
            else 'dummy.xml'
        ),
    ],
    'auto_install': True,
}
