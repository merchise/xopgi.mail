# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-02


dict(
    name='xopgi_unique_message_id',
    version='1.0',
    author='Merchise Autrement',
    category='mail',
    application=False,
    installable=True,
    summary='Mail Hotfix.',
    description=('Avoid Duplicated Message Id on db.'),
    depends=['mail', 'xopgi_mail_threads'],
    data=['data/message_sequence.xml'],
)
