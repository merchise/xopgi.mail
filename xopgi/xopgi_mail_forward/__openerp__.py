#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.__openerp__
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
    'name': 'XOPGI Mail Forward',
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,
    'installable': True,
    'summary': 'Allow to forward messages including the text of the original',
    'depends': ['mail', 'web'],
    'description': '',
    'update_xml': [
        'views/mail_forward_wizard.xml',
    ],
    'css': [
        'static/src/css/mail_forward.css',
    ],
    'js': [
        'static/src/js/mail_forward.js',
    ],
    'qweb': [
        'static/src/xml/mail_forward.xml',
    ],
}
