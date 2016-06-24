#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_move_message
# --------------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

{
    'name': 'XOPGI Mail Move/Copy Messages',
    'version': '1.4',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'summary': 'Add an option to move/mopy existing messages to other mail '
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
        'views/mail_move_message_wizard.xml',
        'views/assets.xml',
    ],
    'css': [
        'static/src/css/mail_move_message.css',
    ],
    'js': [
        'static/src/js/mail_move_message.js',
    ],
    'qweb': [
        'static/src/xml/mail_move_message.xml',
    ],
}
