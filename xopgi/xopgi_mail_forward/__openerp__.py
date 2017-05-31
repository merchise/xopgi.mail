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
    'installable': (8, 0) <= ODOO_VERSION_INFO < (11, 0),   # noqa

    'summary': 'Allow to forward messages including the text of the original',
    'depends': ['mail', 'web'],
    'description': 'In any conversation thread that includes messaging Allow'
                    'to forward messages including the text of the original',
    'data': [
        'views/mail_forward_wizard.xml',
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
    'qweb': [
        'static/src/xml/%d/mail_forward.xml' % ODOO_VERSION_INFO[0],  # noqa
    ],
}
