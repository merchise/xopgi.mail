# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_mail_breaking_cycles.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

{
    "name": "Breaking Cycles (xopgi)",
    "version": "1.0",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_mail_breaking_cycles",
    'category': 'Mail',
    "description": ('Breaking Cycles sending messages.'),
    "depends": ['xopgi_mail_threads', ],
    "data": [],
    "application": False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    "auto_install": True,
}
