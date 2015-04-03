#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# test_verp
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-04-02


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


try:
    from openerp.addons.mail.tests.common import TestMail
except ImportError:
    # OpenERP 7.0
    from openerp.addons.mail.tests.test_mail_base import TestMailBase as TestMail


class TestVERP(TestMail):
    def test_verp_mail(self):
        assert False, 'VERPing'
