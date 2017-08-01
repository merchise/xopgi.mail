#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xopgi_mail_alias_crm
# --------------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# Author: Merchise Autrement [~º/~]
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


from __future__ import absolute_import as _py3_abs_imports

from xoeuf import MAJOR_ODOO_VERSION


if 8 <= MAJOR_ODOO_VERSION < 11:
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import mail_crm  # noqa
