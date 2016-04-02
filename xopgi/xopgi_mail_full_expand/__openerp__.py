#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_expand
# --------------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# flake8: noqa

{
    'name': 'XOPGI Mail Full Expand',
    'version': '1.4',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'summary': 'Add an option to open the mail in a big window.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads'
    ],
    'description': '',
    'data': [
        'views/%d/mail_full_expand_view.xml' % ODOO_VERSION_INFO[0],
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],
    ],
    'css': [
        'static/src/css/%d/mail_full_expand.css' % ODOO_VERSION_INFO[0],
    ],
    'js': [
        'static/src/js/%d/mail_full_expand.js' % ODOO_VERSION_INFO[0],
    ],
    'qweb': [
        'static/src/xml/%d/mail_full_expand.xml' % ODOO_VERSION_INFO[0],
    ],
}
