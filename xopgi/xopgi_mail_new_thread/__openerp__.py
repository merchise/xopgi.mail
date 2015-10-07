#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_expand
# --------------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Eddy Ernesto del Valle Pino <eddy@merchise.org>
# Contributors: see CONTRIBUTORS and HISTORY file
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
    'installable': True,
    'summary': 'Add an option to create new mail capable object from '
               'existing message.',
    'depends': [
        'mail',
        'web',
        'xopgi_mail_threads'
    ],
    'description': '',
    'data': [
        'security/security.xml',
        'views/mail_new_thread_wizard.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/mail_new_thread.xml',
    ],
}
