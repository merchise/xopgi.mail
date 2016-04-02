# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi_evaneos_mailrouter.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

{
    "name": "Evaneos Mail Router (xopgi)",
    "version": "1.4",
    "author": "Merchise Autrement",
    "website": "http://xopgi.merchise.org/addons/xopgi_evaneos_mailrouter",
    'category': 'Social Network',
    "description": ("Improves OpenERP's integration with emails coming via a "
                    "Evaneos. \n\n"
                    "Evaneos removes the 'References' and 'In-Reply-To' "
                    "headers.  This makes it impossible to OpenERP to "
                    "\"follow\" the conversation.  However, since a single "
                    "address is used for the same thread, it is possible to "
                    "assign a thread id based of that field.  \n\n"
                    "This module assign the thread id of the first message "
                    "to incoming messages when they share the same Evaneos "
                    "'From' or 'Sender'."),
    "depends": ['xopgi_mail_threads', ],
    "data": ["data/defaults.xml", ],
    "application": False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (10, 0),   # noqa

}
