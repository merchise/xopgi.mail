#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_alias_project.__openerp__
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# Author: Merchise Autrement [~º/~]
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


{
    'name': 'xopgi_mail_alias_project',
    'version': '1.4',
    'author': 'Merchise Autrement',
    'category': 'mail',
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # WARNING: Although we allow this addon to be installed in Odoo 9 it does
    # not do much.  It's only allowed to ease the migration from Odoo 8 to
    # Odoo 10.
    'installable': ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    'summary': 'Mail Alias Project.',
    'description': 'Extend project module to relate many alias per project to '
               'do different thinks.',
    'depends': [
        'project',
        'project_issue',
        'xopgi_mail_alias'
    ],

    'data': [
         'view/project_view.xml',
         'security/security.xml'
    ] if ODOO_VERSION_INFO[0] in (8, 10) else [],   # noqa
}
