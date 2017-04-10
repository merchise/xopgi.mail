#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_forward.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


{
    'name': 'XOPGI Mail Filters',
    'version': '1.4',
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
        'views/search.xml'
    ],
    'auto_install': True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': ODOO_VERSION_INFO[0] in (8, 10),   # noqa
}
