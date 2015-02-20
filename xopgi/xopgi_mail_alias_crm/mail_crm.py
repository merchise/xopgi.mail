#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_alias_crm.mail_crm
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.osv.orm import Model
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.release import version_info as ODOO_VERSION_INFO

from xoeuf.osv.orm import get_modelname

if ODOO_VERSION_INFO < (8, 0):
    from openerp.addons.crm.crm import crm_case_section as _base
else:
    from openerp.addons.sales_team.sales_team import crm_case_section as _base


def str2dict(dict_str):
    try:
        return dict(eval(dict_str))
    except:
        return {}


class crm_valias(Model):
    _name = 'crm.valias'

    _columns = {
        'alias_name':
            fields.char('Alias', required=True,
                        help="The name of the email alias, e.g. 'jobs' if "
                             "you want to catch emails "
                             "for <jobs@example.my.openerp.com>"),
        'alias_defaults':
            fields.text('Default Values',
                        help="A Python dictionary that will be evaluated to "
                             "provide default values when creating new "
                             "records for this alias."),
        'alias_force_thread_id':
            fields.integer('Record Thread ID',
                           help="Optional ID of a thread (record) to which "
                                "all incoming messages will be attached, "
                                "even if they did not reply to it. If set, "
                                "this will disable the creation of new "
                                "records completely."),
        'type':
            fields.selection([('lead', 'Lead'), ('opportunity', 'Opportunity')],
                             'Type', select=True,
                             help="Type of object to create by incoming "
                                  "messages."),
        'section_id': fields.many2one('crm.case.section', 'Sale Team'),
        'user_id': fields.many2one('res.users', 'Team Leader'),
    }

    def read(self, cr, uid, ids, fields=None, context=None,
             load='_classic_read'):
        """Read the ids from mail.alias if any of fields are not present on
        mail.alias model then search it on alias_defaults dict.

        """
        if context is None:
            context = {}
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        alias_obj = self.pool.get("mail.alias")
        fields2 = []
        other_fields = []
        for field in fields:
            if field in alias_obj._columns.keys():
                fields2.append(field)
            else:
                other_fields.append(field)
        add_default = other_fields and 'alias_defaults' not in fields
        if add_default:
            fields2.append('alias_defaults')
        res = alias_obj.read(cr, uid, ids, fields2, context=context)
        if not other_fields:
            return res
        for row in res:
            defaults = str2dict(row['alias_defaults'])
            for field in other_fields:
                row[field] = defaults.pop(field, False)
            row['alias_defaults'] = str(defaults)
        if add_default:
            [row.pop('alias_defaults', False) for row in res]
        return res


class crm_case_section(Model):
    _inherit = get_modelname(_base)

    def _get_model_id(self, cr, uid, context):
        model_obj = self.pool.get('ir.model')
        return model_obj.search(cr, uid, [('model', '=', 'crm.lead')],
                                context=context)[0]

    def _get_alias(self, cr, uid, ids, field_name=None, arg=None, context=None):
        """Check if each section_ids are referenced on any mail.alias and
        return a list of alias_ids per section_id.
        """
        alias_obj = self.pool.get("mail.alias")
        model_id = self._get_model_id(cr, uid, context=context)
        alias_ids = alias_obj.search(cr, uid, [('alias_model_id', '=',
                                                model_id)],
                                     context=context)

        def _check_one(section_id, alias_id, defaults):
            check = str2dict(defaults).get('section_id', 0)
            if check == section_id:
                return alias_id
            return False

        def _check_all(section_id):
            value = []
            for a in alias_obj.browse(cr, uid, alias_ids, context=context):
                temp = _check_one(section_id, a.id, a.alias_defaults)
                if temp:
                    value.append(temp)
            return value
        return {i: _check_all(i) for i in ids}


    def _unlink_alias(self, cr, uid, section_id, alias_id, context=None):
        alias_obj = self.pool.get("mail.alias")
        section_ids = self.search(cr, uid, [('alias_id', '=', alias_id),
                                            ('active', '=', False),
                                            ('id', '!=', section_id)],
                                  context=context)
        if section_ids:
            self.unlink(cr, uid, section_ids, context=context)
        return alias_obj.unlink(cr, uid, alias_id, context=context)

    def _set_alias(self, cr, uid, section_id, field_name, field_value, arg,
                   context=None):
        alias_obj = self.pool.get("mail.alias")
        model_id = self._get_model_id(cr, uid, context=context)
        CREATE_RELATED = 0
        UPDATE_RELATED = 1
        DELETE_RELATED = 2

        _create = lambda _id, vals: alias_obj.create(cr, uid, vals,
                                                     context=context)
        _write = lambda _id, vals: alias_obj.write(cr, uid, _id, vals,
                                                   context=context)

        def _parse_fields(alias_id, vals):
            '''The fields not present on mail.alias model are include on
            alias_defaults dictionary.

            '''
            fields = []
            other_fields = []
            for field in vals.keys():
                if field in alias_obj._columns.keys():
                    fields.append(field)
                else:
                    other_fields.append(field)
            if not other_fields:
                return vals
            defaults = '{}'
            if 'alias_defaults' in fields:
                defaults = str2dict(vals['alias_defaults'])
            elif alias_id:
                row = alias_obj.read(cr, uid, alias_id,
                                     ['alias_defaults'], context=context)
                defaults = str2dict(row['alias_defaults'])
            for field in other_fields:
                value = vals.pop(field, False)
                if value:
                    defaults.update({field: value})
            vals['alias_defaults'] = str(defaults)
            if ODOO_VERSION_INFO < (8, 0):
                return vals
            _type = vals.get('type', False)
            if not _type:
                return vals
            section = self.browse(cr, uid, section_id, context=context)
            if (not section.use_leads) and _type == 'lead':
                raise osv.except_osv(_('Warning!'), _(
                    "This sale team not use leads then cant alias with"
                    "leads creation."))
            if (not section.use_opportunities) and _type == 'opportunity':
                raise osv.except_osv(_('Warning!'), _(
                    "This sale team not use opportunity then cant alias with"
                    "opportunities creation."))
            return vals

        def _action(_id, vals, _function):
            vals['section_id'] = section_id
            section = self.browse(cr, uid, section_id, context=context)
            vals['user_id'] = (section.user_id.id
                               if section and section.user_id
                               else False)
            vals = _parse_fields(_id, vals)
            vals['alias_model_id'] = model_id
            return _function(_id, vals)
        to_unlink = []
        for option, alias_id, values in field_value:
            if option == CREATE_RELATED:
                _action(False, values, _create)
            elif option == UPDATE_RELATED:
                _action(alias_id, values, _write)
            elif option == DELETE_RELATED:
                to_unlink.append(alias_id)
        if to_unlink:
            self._unlink_alias(cr, uid, section_id, to_unlink, context=context)
        return 1

    _columns = {
        'alias_ids': fields.function(
            _get_alias,
            fnct_inv=_set_alias,
            method=True,
            relation='crm.valias',
            string='Mail Aliases',
            type='one2many',
            help=("The email addresses associated "
                  "with this team. New emails "
                  "received will automatically "
                  "create new Lead/Opportunity "
                  "assigned to the team.")),
    }

    def create(self, cr, uid, values, context=None):
        """Check if at least one mail alias is defined, create a temporal alias to
        avoid create the default one, replace the temporal alias by user
        defined ones and remove the temporal alias.  Else if no mail alias are
        defined let create de default one.

        """
        if context is None:
            context = {}
        if values.get('alias_ids', False):
            alias_obj = self.pool.get("mail.alias")
            temp_alias = alias_obj.create_unique_alias(
                cr, uid,
                {'alias_name': 'crm+temp-alias'},
                model_name="crm.lead",
                context=context
            )
            values['alias_id'] = temp_alias
            values.pop('alias_name', None)
        else:
            temp_alias = False
        res = super(crm_case_section, self).create(cr, uid, values,
                                                   context=context)
        if temp_alias:
            alias_ids = self._get_alias(cr, uid, [res], context=context)[res]
            if temp_alias in alias_ids:
                alias_ids.remove(temp_alias)
            self.write(cr, uid, res, {'alias_id': alias_ids[0]}, context=context)
            self.pool['mail.alias'].unlink(cr, uid, temp_alias, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """Cascade unlink the mail alias related.

        """
        if context is None:
            context = {}
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        alias_ids = self._get_alias(cr, uid, ids, context=context)
        result = super(crm_case_section, self).unlink(cr, uid, ids,
                                                      context=context)
        for _id, _ids in alias_ids.items():
            if _ids:
                self._unlink_alias(cr, uid, _id, _ids, context=context)
        return result
