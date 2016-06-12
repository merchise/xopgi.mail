#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_filter.mail_config
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-04-03

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from datetime import datetime
from openerp.osv.orm import Model
from openerp.release import version_info as ODOO_VERSION_INFO
from xoeuf.osv.model_extensions import search_browse

MODULE_NAME = 'xopgi_mail_filter'


def followed_models(cr):
    '''Get all model's names with at less one follower related.

    '''
    cr.execute('SELECT res_model FROM mail_followers GROUP BY res_model')
    return [row[0] for row in cr.fetchall()]


class MailConfig(Model):
    _inherit = 'base.config.settings'

    def extend_search_views(self, cr, uid, context=None):
        '''Get all primary search views from all actual followed models
        and add it a message_follower_ids field filter.

        '''
        insert_query = '''
            INSERT INTO ir_ui_view (%(columns)s)
            VALUES (%(values)s);
             '''
        columns = ['model', 'type', 'arch', 'priority', 'create_uid',
                   'create_date', 'write_date', 'write_uid', 'inherit_id',
                   'name']
        view_values = ['%s', "'search'",
                       '\'<?xml version="1.0"?>\n'
                       '<xpath expr="/search" position="inside">\n'
                       ' <field name="message_follower_ids"/>\n'
                       '</xpath>\'', str(16), str(uid),
                       "'%s'" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       "'%s'" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       str(uid), '%s', '%s']
        if ODOO_VERSION_INFO >= (8, 0):
            columns.extend(['mode', 'active'])
            view_values.extend(["'extension'", str(True)])
        insert_query = insert_query % dict(columns=', '.join(columns),
                                           values=', '.join(view_values))
        models = followed_models(cr)
        view_obj = self.pool['ir.ui.view']
        args = [('model', 'in', models), ('inherit_id', '=', False),
                ('type', '=', 'search')]
        for view in search_browse(view_obj, cr, uid, args, context=context):
            name = "%s.%s.followers.filter" % (MODULE_NAME, view.model)
            check_args = [('model', '=', view.model), ('inherit_id', '=', view.id),
                          ('type', '=', 'search'), ('name', '=', name)]
            if not view_obj.search(cr, uid, check_args, context=context):
                cr.execute(insert_query, (view.model, view.id, name))
        return True

    def add_followers_filter(self, cr, uid, ids, context=None):
        '''Method called by config button for add followers filters.

        '''
        self.extend_search_views(cr, uid, context=context)
        return {'type': 'ir.actions.client', 'tag': 'reload', }
