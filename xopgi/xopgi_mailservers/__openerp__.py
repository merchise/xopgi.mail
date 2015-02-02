#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-01-22

dict(
    name="Same server policy",
    version="1.0",
    author="Merchise Autrement",
    category="Hidden",
    depends=["xopgi_mail_threads"],
    description='Send emails via the right SMTP server. ',
    data=[
        'views/server.xml',
    ],
    application=False,
    installable=True,
    auto_install=False,
)
