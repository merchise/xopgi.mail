# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.__openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-21

from openerp.release import version_info as ODOO_VERSION_INFO

if ODOO_VERSION_INFO < (9, 0):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import models  # noqa
    from . import wizards  # noqa
