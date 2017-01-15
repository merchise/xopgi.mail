#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_new_thread
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.

{
    'name': 'XOPGI Mail New Thread',
    'version': '1.4',
    "author": 'Merchise Autrement',
    'category': 'Social Network',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # BIG WARNING: Although we make this installable in Odoo 9, it's done so
    # for the sake of easy migrations.  This addon won't work in Odoo 9.
    'installable': ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    'summary': 'Add an option to create new mail capable object from '
               'existing message.',
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
        'views/%d/mail_new_thread_wizard.xml' % ODOO_VERSION_INFO[0],  # noqa
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_new_thread.xml' % ODOO_VERSION_INFO[0]  # noqa
    ],
}
