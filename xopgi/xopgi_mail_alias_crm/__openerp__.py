#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_alias_crm.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Merchise Autrement
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


{
    'name': 'xopgi_mail_alias_crm',
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'mail',
    'application': False,
    'installable': True,
    'summary': 'Extend crm module to relate many alias per sale team.',
    'depends': ['crm', 'xopgi_mail'],
    'data': [
        'view/crm_view.xml'
    ],
}
