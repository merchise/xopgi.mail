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


from xoeuf import fields, api, models
from xoeuf.odoo import tools
from xoeuf.odoo.addons.xopgi_mail_threads.utils import decode_header
from xoeuf.odoo.addons.xopgi_mail_threads import MailRouter


def get_default_alias_domain(self):
    get_param = self.env['ir.config_parameter'].get_param
    res = get_param('mail.catchall.domain', '')
    return res


class MailAlias(models.Model):
    _inherit = 'mail.alias'

    custom_domain = fields.Char('Alias domain')
    alias_domain = fields.Char(
        compute='_get_alias_domain',
        inverse='_set_alias_domain',
        search='_search_alias_domain',
        string="Alias domain",
        default=get_default_alias_domain
    )

    @api.multi
    def _get_alias_domain(self):
        default_domain = get_default_alias_domain(self)
        for record in self:
            record.alias_domain = record.custom_domain or default_domain

    @api.model
    def _search_alias_domain(self, args):
        res = []
        for cond in args:
            new_arg = cond
            if len(new_arg) == 3 and new_arg[0] == 'alias_domain':
                new_arg = ['custom_domain'] + list(cond)[1:]
            res.append(new_arg)
        return res

    @api.multi
    def _set_alias_domain(self):
        for record in self:
            self.custom_domain = self.alias_domain

    def fields_get(self, *args, **kargs):
        # Hack to make alias_domain editable. I don't know why it's not!
        result = super(MailAlias, self).fields_get(*args, **kargs)
        alias_domain = result.get('alias_domain', None)
        if alias_domain:
            alias_domain['readonly'] = 0
        return result


class AliasMailRouter(MailRouter):
    @classmethod
    def query(cls, obj, message):
        return True, None

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        result = []
        rcpt_tos = tools.email_split(
            ','.join([decode_header(message, 'Delivered-To'),
                      decode_header(message, 'To'),
                      decode_header(message, 'Cc'),
                      decode_header(message, 'Resent-To'),
                      decode_header(message, 'Resent-Cc')])
        )
        for route in routes:
            alias = route[-1] if len(route) == 5 else None
            if alias:
                if alias.alias_domain:
                    alias_mail = '%s@%s' % (alias.alias_name, alias.alias_domain)
                    if rcpt_tos and any(alias_mail.lower() == rcpt.lower() for rcpt in rcpt_tos):
                        result.append(route)
                else:
                    result.append(route)
            else:
                result.append(route)
        routes[:] = result
        return routes
