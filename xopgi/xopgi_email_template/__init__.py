#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from xoeuf import MAJOR_ODOO_VERSION


if MAJOR_ODOO_VERSION in (8, 9, 10):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import models  # noqa
    from . import wizards  # noqa
