#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_cc_save
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-07-06
# flake8: noqa

dict(
    name="Cuba Autrement CC save",
    summary="Save all original recipients on incoming messages",
    version="1.0",
    author="Merchise Autrement",
    website="",
    category="Social Network",
    depends=['mail', 'xopgi_mail_threads', 'xopgi_mail_full_expand'],
    data=[
        'views/mail_message_views.xml'
    ],
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),
)
