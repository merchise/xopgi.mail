#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
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
    'installable': MAJOR_ODOO_VERSION in (8, 9, 10),   # noqa

    "auto_install": True,
}
