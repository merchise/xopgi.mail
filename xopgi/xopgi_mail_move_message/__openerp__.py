#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': 'XOPGI Mail Move/Copy Messages',
    'version': '1.4',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    'summary': 'Add an option to move/mopy existing messages to other mail'
               'threads.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads',
        'xopgi_move_copy_msg_commons'
    ],
    'description': '',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/%d/mail_move_message_wizard.xml' % MAJOR_ODOO_VERSION,  # noqa
        'views/%d/assets.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_move_message.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],

}
