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

try:
    from odoo.release import version_info as VERSION_INFO
except ImportError:  # Odoo 10+
    from openerp.release import version_info as VERSION_INFO

from . import test_verp


if VERSION_INFO < (8, 0):
    checks = [
        test_verp,
    ]
