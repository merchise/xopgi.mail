#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# common
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-16

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.release import version_info as ODOO_VERSION_INFO


def get_bounce_alias(pool, cr, uid, context=None):
    alias_name = ('mail.catchall.alias'
                  if ODOO_VERSION_INFO < (8, 0)
                  else 'mail.bounce.alias')
    get_param = pool['ir.config_parameter'].get_param
    return get_param(cr, uid, alias_name,
                     default='postmaster-odoo', context=context)
