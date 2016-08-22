# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_move_copy_msg_commons.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-02-13


{
    'name': 'Move Message commons',
    'version': '1.0',
    "author": 'Merchise Autrement',
    'category': 'Internal',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'summary': 'Add method to move messages.',
    'depends': [
        'mail',
        'xopgi_mail_threads',
    ],
    'description': '',
    'data': ['views/config.xml',
             'security/ir.model.access.csv',
            ],
}
