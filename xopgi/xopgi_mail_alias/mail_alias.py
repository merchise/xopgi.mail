# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.router
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.models import Model
from openerp.osv import fields
from openerp.addons.xopgi_mail_threads import MailRouter
from openerp.addons.mail.mail_thread import decode_header
from openerp import tools


def get_default_alias_domain(pool, cr, uid, context=None):
    '''

    '''
    get_param = pool['ir.config_parameter'].get_param
    res = get_param(cr, uid, 'mail.catchall.domain', '', context=context)
    return res


class MailAlias(Model):
    _inherit = 'mail.alias'

    def _get_alias_domain(self, cr, uid, ids, name, args, context=None):
        default_domain = get_default_alias_domain(self.pool, cr, uid,
                                                  context=context)
        res = dict.fromkeys(ids, default_domain or "")
        cr.execute(
            'SELECT id, custom_domain FROM mail_alias WHERE id in %s',
            (tuple(ids),))
        res.update({_id: domain for _id, domain in cr.fetchall()
                    if domain})
        return res

    def _search_alias_domain(self, cr, uid, obj, name, args, context):
        res = []
        for cond in args:
            new_arg = cond
            if len(new_arg) == 3 and new_arg[0] == 'alias_domain':
                new_arg = ['custom_domain'] + list(cond)[1:]
            res.append(new_arg)
        return res

    def _set_alias_domain(self, cr, uid, ids, name, value, arg, context=None):
        self.write(cr, uid, ids, {'custom_domain': value}, context=context)

    _columns = dict(
        custom_domain=fields.char('Alias domain'),
        alias_domain=fields.function(_get_alias_domain,
                                     fnct_inv=_set_alias_domain,
                                     fnct_search=_search_alias_domain,
                                     string="Alias domain",
                                     type='char'),
    )

    _defaults = dict(
        alias_domain=lambda s, c, u, ctx: get_default_alias_domain(
            s.pool, c, u, context=ctx)
    )

    def fields_get(self, *args, **kargs):
        # Hack to make alias_domain editable. I don't know why it's not!
        result = super(MailAlias, self).fields_get(*args, **kargs)
        alias_domain = result.get('alias_domain', None)
        if alias_domain:
            alias_domain['readonly'] = 0
        return result


class AliasMailRouter(MailRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        return True, None

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
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
                alias_mail = '%s@%s' % (alias.alias_name, alias.alias_domain)
                if rcpt_tos and any(alias_mail == rcpt for rcpt in rcpt_tos):
                    result.append(route)
            else:
                result.append(route)
        routes[:] = result
        return routes
