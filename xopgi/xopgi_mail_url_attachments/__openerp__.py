# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_url_attachments.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-23


{
    'name': "Add URL attachments from incoming messages.",
    'version': '1.0',
    'author': 'Merchise Autrement',
    'category': 'Marketing',
    'depends': ['xopgi_mail_threads'],
    'description': "Add URL attachments from links on messages body.",
    'data': [],
    'demo': [],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'images': [],
}
