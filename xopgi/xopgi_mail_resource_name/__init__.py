#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print)

from xoeuf import models, api
from xoeuf import MAJOR_ODOO_VERSION


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def get_resource_action(self):
        model = self.model
        res_id = self.res_id
        if model and res_id:
            resource = self.env[model].browse(res_id)
        if MAJOR_ODOO_VERSION < 9:
            # Since Odoo 9 the method get_access_action in models.py now
            # returns a single dictionary.
            _result = dict(resource.get_access_action()[0])
        else:
            _result = dict(resource.get_access_action())
        return _result
