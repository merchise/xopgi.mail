#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from lxml.html import fromstring as html_fromstring

from xoeuf import api, fields, models, MAJOR_ODOO_VERSION


class EmailTemplate(models.Model):
    _inherit = 'email.template' if MAJOR_ODOO_VERSION < 9 else 'mail.template'

    use_default_subject = fields.Boolean()

    @api.one
    def get_body_readonly_elements(self, res_id):
        if MAJOR_ODOO_VERSION < (10, 0):
            _super = super(EmailTemplate, self).generate_email_batch
        else:
            _super = super(EmailTemplate, self).generate_email
        msg_dict = _super([self.res_id], fields=['body_html'])
        template_body = msg_dict.get(res_id, {}).get('body_html')
        if not template_body:
            return []
        html_element = html_fromstring(template_body)
        return html_element.find_class('readonly')
