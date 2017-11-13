#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp.release import version_info as ODOO_VERSION_INFO


if ODOO_VERSION_INFO < (9, 0):
    from . import no_autofollow  # noqa
