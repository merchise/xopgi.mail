#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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
    'installable': MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

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
        'views/%d/mail_new_thread_wizard.xml' % MAJOR_ODOO_VERSION,  # noqa
        'views/%d/assets.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_new_thread.xml' % MAJOR_ODOO_VERSION  # noqa
    ],
}
