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


# The name of the configuration parameter where the alias for bounces should
# be located.
MAIL_BOUNCE_ALIAS_PARAM = 'mail.bounce.alias'

# The name of the preferred alias for VERP bounces.  If this alias is set the
# 'mail.bounces.alias' won't be used.  This allows to bypass the Odoo
# mail.mail default Return-Path, though VERP is not installed.
MAIL_BOUNCE_VERP_ALIAS_PARAM = 'mail.bounce.verp.alias'

# The default alias.
DEFAULT_BOUNCE_ALIAS = 'postmaster-odoo'


def get_bounce_alias(pool, cr, uid, context=None):
    '''Return the alias for building bouncing addresses.

    If no alias are set, return 'postmaster-odoo'.

    '''
    alias_name = ('mail.catchall.alias'
                  if ODOO_VERSION_INFO < (8, 0)
                  else MAIL_BOUNCE_ALIAS_PARAM)
    get_param = pool['ir.config_parameter'].get_param
    bounce = get_param(cr, uid, alias_name,
                       default=DEFAULT_BOUNCE_ALIAS, context=context)
    res = get_param(cr, uid, MAIL_BOUNCE_VERP_ALIAS_PARAM, default=bounce,
                    context=context)
    return res
