# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.models.email_template
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-21

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from lxml.html import fromstring

from openerp import api, fields, models


class EmailTempla(models.Model):
    _inherit = 'email.template'

    use_default_subject = fields.Boolean()

    @api.one
    def get_body_readonly_elements(self, res_id):
        msg_dict = super(EmailTempla, self).generate_email_batch(
            [self.res_id], fields=['body_html'])
        template_body = msg_dict.get(res_id, {}).get('body_html')
        if not template_body:
            return []
        html_element = fromstring(template_body)
        return html_element.find_class('readonly')
