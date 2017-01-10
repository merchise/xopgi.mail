#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
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
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'Hidden',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'summary': 'Allow to forward messages including the text of the original',
    'depends': ['mail', 'web'],
    'description': '',
    'data': [
        'views/mail_forward_wizard.xml',
        (
            'views/assets.xml'
            if ODOO_VERSION_INFO >= (8, 0)  # noqa
            else 'views/dummy.xml'
        ),
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
