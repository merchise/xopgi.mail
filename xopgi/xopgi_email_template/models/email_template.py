# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.models.email_template
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-21
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