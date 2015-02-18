#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_alias_project.mail_project
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

from xoeuf.osv.orm import get_modelname
from openerp.addons.project.project import project as _base


def str2dict(dict_str):
    try:
        return dict(eval(dict_str))
    except Exception:
        return {}


def _get_model_ids(cr, uid, model_names=[], context=None):
    from openerp import pooler
    model_obj = pooler.get_pool(cr.dbname)['ir.model']
    model_names = model_names if model_names else ['project.task',
                                                   'project.issue']
    return model_obj.search(cr, uid, [('model', 'in', model_names)],
                            context=context)


class project_valias(Model):
    _name = 'project.valias'

    def _get_models(self, cr, uid, context=None):
        model_ids = _get_model_ids(cr, uid, context=context)
        return self.pool['ir.model'].name_get(cr, uid, model_ids, context=context)

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
        'alias_model_id':
            fields.selection(_get_models, 'Aliased Model',
                             required=True,
                             help="The model (OpenERP Document Kind) to "
                                  "which this alias corresponds. Any "
                                  "incoming email that does not reply to an "
                                  "existing record will cause the creation "
                                  "of a new record of this model "
                                  "(e.g. a Project Task)"),
        'project_id': fields.many2one('project.project', 'Project'),
        'user_id': fields.many2one('res.users', 'Project Manager'),
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


class project_project(Model):
    _inherit = get_modelname(_base)

    def _get_alias(self, cr, uid, ids, field_name=None, arg=None, context=None):
        """Check if each section_ids are referenced on any mail.alias and
        return a list of alias_ids per section_id.
        """
        alias_obj = self.pool.get("mail.alias")
        model_ids = _get_model_ids(cr, uid, context=context)
        alias_ids = alias_obj.search(cr, uid,
                                     [('alias_model_id', 'in', model_ids)],
                                     context=context)

        def _check_one(project_id, alias_id, defaults):
            check = str2dict(defaults).get('project_id', 0)
            if check == project_id:
                return alias_id
            return False

        def _check_all(project_id):
            value = []
            for alias in alias_obj.browse(cr, uid, alias_ids, context=context):
                temp = _check_one(project_id, alias.id, alias.alias_defaults)
                if temp:
                    value.append(temp)
            return value
        return {i: _check_all(i) for i in ids}

    def _unlink_alias(self, cr, uid, project_id, alias_id, context=None):
        alias_obj = self.pool.get("mail.alias")
        project_ids = self.search(cr, uid, [('alias_id', '=', alias_id),
                                            ('active', '=', False),
                                            ('id', '!=', project_id)],
                                  context=context)
        if project_ids:
            self.unlink(cr, uid, project_ids, context=context)
        return alias_obj.unlink(cr, uid, alias_id, context=context)

    def _set_alias(self, cr, uid, project_id, field_name, field_value, arg,
                   context=None):
        alias_obj = self.pool.get("mail.alias")
        CREATE_RELATED = 0
        UPDATE_RELATED = 1
        DELETE_RELATED = 2

        def _parse_fields(_id, vals):
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
            elif _id:
                row = alias_obj.read(cr, uid, _id,
                                     ['alias_defaults'], context=context)
                defaults = str2dict(row['alias_defaults'])
            defaults.update({field: vals.pop(field, False)
                             for field in other_fields
                             if vals.get(field, False)})
            vals['alias_defaults'] = str(defaults)
            model_id = vals.get('alias_model_id', False)
            if not model_id:
                return vals
            project = self.browse(cr, uid, project_id, context=context)
            if ((not project.use_issues) and
                        model_id == _get_model_ids(cr, uid, ['project.issue'],
                                                   context=context)):
                raise osv.except_osv(_('Warning!'), _(
                    "This project not use issues then cant alias with"
                    "project.issue object creation."))
            if ((not project.use_tasks) and
                        model_id == _get_model_ids(cr, uid, ['project.task'],
                                                   context=context)):
                raise osv.except_osv(_('Warning!'), _(
                    "This project not use tasks then cant alias with"
                    "project.task object creation."))
            return vals

        def _write(_id, vals):
            vals = _parse_fields(_id, vals)
            return alias_obj.write(cr, uid, _id, vals, context=context)

        def _create(vals):
            if not vals.get('project_id', False):
                vals['project_id'] = project_id
                project = self.browse(cr, uid, project_id, context=context)
                vals['user_id'] = (project.user_id.id
                                   if project and project.user_id
                                   else False)
            vals = _parse_fields(False, vals)
            return alias_obj.create(cr, uid, vals, context=context)
        to_unlink = []
        for option, alias_id, values in field_value:
            if option == CREATE_RELATED:
                _create(values)
            elif option == UPDATE_RELATED:
                _write(alias_id, values)
            elif option == DELETE_RELATED:
                to_unlink.append(alias_id)
        if to_unlink:
            self._unlink_alias(cr, uid, project_id, to_unlink, context=context)
        return 1

    _columns = {
        'alias_ids': fields.function(_get_alias,  fnct_inv=_set_alias,
                                     method=True, relation='project.valias',
                                     string='Mail Aliases',
                                     type='one2many',
                                     help="The email addresses associated "
                                          "with this project. New emails "
                                          "received will automatically "
                                          "create new Task/Issues "
                                          "assigned to the project."),
    }

    def create(self, cr, uid, values, context=None):
        """Check if at lees one mail alias is defined, create a temporal
        alias to avoid create the default one, replace
        the temporal alias by user defined ones and remove de temporal
        alias. Else if not mail alias are defined let create de default one.

        """
        if context is None:
            context = {}
        temp_alias = False
        alias_obj = self.pool.get("mail.alias")
        if values.get('alias_ids', False):
            temp_alias = alias_obj.create_unique_alias(cr, uid,
                                                       {'alias_name':
                                                            'project+temp-alias'},
                                                       model_name="project.task",
                                                       context=context)
            values['alias_id'] = temp_alias
            values.pop('alias_name', None)
        res = super(project_project, self).create(cr, uid, values, context=context)
        if temp_alias:
            alias_ids = self._get_alias(cr, uid, [res], context=context)[res]
            if temp_alias in alias_ids:
                alias_ids.remove(temp_alias)
            self.write(cr, uid, res, {'alias_id': alias_ids[0]}, context=context)
            alias_obj.unlink(cr, uid, temp_alias, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """Cascade unlink the mail alias related.

        """
        if context is None:
            context = {}
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        alias_ids = self._get_alias(cr, uid, ids, context=context)
        result = super(project_project, self).unlink(cr, uid, ids, context=context)
        for _id, _ids in alias_ids.items():
            if _ids:
                self._unlink_alias(cr, uid, _id, _ids, context=context)
        return result