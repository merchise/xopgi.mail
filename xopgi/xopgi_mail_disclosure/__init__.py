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

from xoeuf import MAJOR_ODOO_VERSION


if 8 <= MAJOR_ODOO_VERSION < 11:
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import disclose  # noqa
