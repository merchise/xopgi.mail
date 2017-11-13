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


if ODOO_VERSION_INFO[0] in (8, 9, 10):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import models  # noqa
    from . import wizards  # noqa
