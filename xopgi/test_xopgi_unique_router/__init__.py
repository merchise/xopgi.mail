#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import models
from xoeuf.odoo import api, SUPERUSER_ID

TEST_DOMAIN = 'example.com'


class Model(models.Model):
    _name = 'test_xopgi_unique_router.model'
    _inherit = ['mail.thread']


def _assert_test_mode(cr, registry, *args):
    from xoeuf import odoo
    if not odoo.tools.config['test_enable']:
        raise RuntimeError('You cannot install a test addon in a production DB')
    env = api.Environment(cr, SUPERUSER_ID, {})
    get_param = env['ir.config_parameter'].get_param
    domain = get_param('mail.catchall.domain')
    if domain and domain != TEST_DOMAIN:
        env['ir.config_parameter'].set_param('mail.catchall.domain',
                                             TEST_DOMAIN)
    elif not domain:
        env['ir.config_parameter'].sudo().create(
            dict(key='mail.catchall.domain', value=TEST_DOMAIN))
