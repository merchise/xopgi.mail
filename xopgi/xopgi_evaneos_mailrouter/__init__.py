# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_evaneos_mailrouter
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-22

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp.release import version_info as ODOO_VERSION_INFO


if ODOO_VERSION_INFO[0] in (8, 10):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import router  # noqa
