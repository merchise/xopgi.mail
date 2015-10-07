#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_expand
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
    'name': 'XOPGI Mail Full Expand',
    'version': '1.4',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,
    'installable': True,
    'summary': 'Add an option to open the mail in a big window.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads'
    ],
    'description': '',
    'data': [
        'views/mail_full_expand_view.xml',
        (
            'views/assets.xml'
            if ODOO_VERSION_INFO >= (8, 0)  # noqa
            else 'views/dummy.xml'
        ),
    ],
    'css': [
        'static/src/css/mail_full_expand.css',
    ] if ODOO_VERSION_INFO < (8, 0) else [],   # noqa
    'js': [
        'static/src/js/mail_full_expand.js',
    ] if ODOO_VERSION_INFO < (8, 0) else [],   # noqa
    'qweb': [
        'static/src/xml/mail_full_expand.xml',
    ],
}
