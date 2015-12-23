#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_verp.__openerp__
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


dict(
    name='xopgi_mail_verp',
    version='2.0',
    author='Merchise Autrement',
    category='mail',
    application=False,
    installable=True,
    summary='Variable Envelop Return Path (VERP)',
    description=('Allows to track email bounces and add them to the '
                 'proper thread.'),
    depends=['mail', 'xopgi_mail_threads'],
    external_dependencies={'python': ['flufl.bounce']},
    data=['data/cron.xml', 'data/acl.xml'],
)
