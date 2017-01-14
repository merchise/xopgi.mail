# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xhg_ca_coordination_board.reports.confirmation_time
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2016-02-20

try:
    from openerp.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from odoo.release import version_info as ODOO_VERSION_INFO


if ODOO_VERSION_INFO < (9, 0):
    from . import no_autofollow  # noqa
