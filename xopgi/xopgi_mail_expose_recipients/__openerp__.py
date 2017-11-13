#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
# flake8: noqa

dict(
    name="Expose original recipients of incoming messages",
    summary="Save all original recipients of incoming messages",
    version="1.0",
    author="Merchise Autrement",
    website="",
    category="Social Network",
    depends=[
        'mail',
        'xopgi_mail_threads',
        'xopgi_mail_full_expand'
    ],
    data=[
         'views/mail_message_views.xml'
    ],
    installable=ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa
)
