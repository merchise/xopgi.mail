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

# The default alias.
DEFAULT_BOUNCE_ALIAS = 'postmaster-odoo'


def get_bounce_alias(pool, cr, uid, context=None):
    '''Return the alias for building bouncing addresses.

    Will try to the alias from the MAIL_BOUNCE_ALIAS_PARAM, if not defined we
    fall back to the 'mail.catchall.alias' (only in OpenERP).

    If no alias is defined, return 'postmaster-odoo'.

    '''
    alias_name = ('mail.catchall.alias'
                  if ODOO_VERSION_INFO < (8, 0)
                  else MAIL_BOUNCE_ALIAS_PARAM)
    get_param = pool['ir.config_parameter'].get_param
    res = get_param(cr, uid, alias_name,
                    default=DEFAULT_BOUNCE_ALIAS, context=context)
    return res
