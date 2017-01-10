#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_resource_name
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-08-31

from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print)

from openerp import models, api


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def get_resource_action(self):
        model = self.model
        res_id = self.res_id
        if model and res_id:
            resource = self.env[model].browse(res_id)
            return dict(resource.get_access_action()[0])
