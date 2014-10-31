#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_expand
# --------------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
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
    'version': '1.0',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,
    'installable': True,
    'summary': 'Add an option to open the mail in a big window.',
    'depends': ['mail', 'web'],
    'description': '''''',
    'data': [
        'mail_full_expand_view.xml',
    ],
    'css': [
        'static/src/css/mail_full_expand.css',
    ],
    'js': [
        'static/src/js/mail_full_expand.js',
    ],
    'qweb': [
        'static/src/xml/mail_full_expand.xml',
    ],
}
