#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_alias_project.mail_project
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo import models, fields, exceptions
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp import models, fields, exceptions
    from openerp.release import version_info as ODOO_VERSION_INFO


from xoeuf import api


def _get_model_ids(self, model_names=[]):
    model_obj = self.env['ir.model']
    model_names = model_names if model_names else ['project.task', 'project.issue']
    return model_obj.search([('model', 'in', model_names)])


# TODO: Design for unity: Don't repeat concepts.  This model and the
# crm.valias are very similar (the read is just the same).  Put similar things
# in a superclass.  See for instance the file
# `xopgi.account/xopgi/xopgi_account/multicompanyitem.py`.

class project_valias(models.Model):
    _name = 'project.valias'
    _inherit = ['xopgi.mail.alias.mocker']

    @api.model
    def _get_models(self):
        models = _get_model_ids(self)
        return models.name_get()

    alias_model_id = fields.Selection(
        _get_models,
        'Aliased Model',
        required=True,
        help=("The model (OpenERP Document Kind) to "
              "which this alias corresponds. Any "
              "incoming email that does not reply to an "
              "existing record will cause the creation "
              "of a new record of this model "
              "(e.g. a Project Task)")
    )

    project_id = fields.Many2one('project.project', string='Project')
    user_id = fields.Many2one('res.users', string='Project Manager')


class project_project(models.Model):
    _inherit = _name = 'project.project'

    @api.multi
    def _get_alias(self):
        """Check if each section_ids are referenced on any mail.alias and
        return a list of alias_ids per section_id.
        """
        Alias = self.env['mail.alias']
        Virtual = self.env['project.valias']
        models = _get_model_ids(self)
        for record in self:
            aliases = Alias.search([('alias_model_id', 'in', models.ids)])\
                           .filtered(lambda a: eval(a.alias_defaults).get('project_id', 0) == record.id)\
                           .mapped('id')
            record.alias_ids = Virtual.browse(aliases)

    @api.multi
    def _unlink_alias(self, alias_id):
        Alias = self.env['mail.alias']
        projects = self.search([('alias_id', '=', alias_id),
                                ('active', '=', False),
                                ('id', '!=', self.id)])
        if projects:
            projects.unlink()
        return Alias.browse(alias_id).unlink()

    def validate_model_project(self, vals, use_issue, use_task):
        """Validate that when creating a mail_alias within a project is not
           created or modified with a model (Task, Issues) without being
           defined for that project that can use Task and Issues.
        """
        model_id = vals.get('alias_model_id', False)
        if not model_id:
            return vals
        if use_issue is None:
            use_issue = self.use_issues
        if use_task is None:
            use_task = self.use_tasks
        if not use_issue and model_id == _get_model_ids(self, ['project.issue']).id:
            raise exceptions.Warning(
                "This project not use 'Issues' then cant alias with 'project.issue'"
                " please select the 'Isuues option' from the project form.")
        if not use_task and model_id == _get_model_ids(self, ['project.task']).id:
            raise exceptions.Warning(
                "This project not use 'Tasks' then cant alias with 'project.task'"
                " please select the 'Tasks option' from the project form.")
        return vals

    @api.multi
    def _set_alias(self):
        pass

    def set_values(self, field_value, use_issue, use_task):
        """It manages the CRUD of mail aliases for a project. In the case of
        "create" it returns a list of the identifiers of the new mail alias
        that have been created. In the case of write and unlink it returns an
        empty list.
        """
        from xoeuf.osv.orm import CREATE_RELATED, UPDATE_RELATED, REMOVE_RELATED
        Alias = self.env['mail.alias']
        Virtual = self.env['project.valias']

        def update_values(id, vals):
            vals['project_id'] = self.id
            vals['user_id'] = self.user_id.id
            vals = Virtual._parse_fields(id, vals)
            vals = self.validate_model_project(vals, use_issue, use_task)
            return vals

        def create_mail_alias(alias_id, values):
            return Alias.create(update_values(alias_id, values))

        def update_mail_alias(alias_id, values):
            return Alias.browse(alias_id).write(update_values(alias_id, values))

        to_unlink = []
        alias_add = []
        for option, alias_id, values in field_value:
            if option == CREATE_RELATED:
                alias = create_mail_alias(alias_id, values)
                alias_add.append(alias.id)
            elif option == UPDATE_RELATED:
                update_mail_alias(alias_id, values)
            elif option == REMOVE_RELATED:
                to_unlink.append(alias_id)
        if to_unlink:
            self._unlink_alias(to_unlink)
        return alias_add

    alias_ids = fields.One2many(
        'project.valias',
        compute='_get_alias',
        inverse='_set_alias',
        string='Mail Aliases',
        help=("The email addresses associated "
              "with this project. New emails "
              "received will automatically "
              "create new Task/Issues "
              "assigned to the project.")
    )

    @api.model
    def create(self, values):
        """Odoo create by deafault a mail alias.This function allows you to
           create more than one mail alias since a project is created for the
           first time.
        """
        from xoutil.string import normalize_slug
        if not values.get('alias_name'):
            values['alias_name'] = normalize_slug(values['name'])
        if ODOO_VERSION_INFO < (10, 0):
            Alias = self.env['mail.alias']
            vals = {}
            if 'alias_ids' in values:
                valias = values.pop('alias_ids')
                use_issue = values.get('use_issues', None)
                use_task = values.get('use_tasks', None)
                aliases_create = self.set_values(valias, use_issue, use_task)
            else:
                aliases_create = []
            project = super(project_project, self).create(values)
            if project and aliases_create:
                for alias in aliases_create:
                    record = Alias.browse(alias)
                    values_default = eval(record.alias_defaults)
                    values_default.update(project_id=project.id, user_id=project.user_id.id)
                    vals['alias_defaults'] = repr(values_default)
                    record.write(vals)
        if ODOO_VERSION_INFO > (9, 0):
            project = super(project_project, self).create(values)
        return project

    @api.multi
    def write(self, values):
        """Override the project for to update relation of valias-project
        """
        if 'alias_ids' in values:
            valias = values.pop('alias_ids')
            use_issue = values.get('use_issues', None)
            use_task = values.get('use_tasks', None)
            self.set_values(valias, use_issue, use_task)
        return super(project_project, self).write(values)

    @api.multi
    def unlink(self):
        """Unlink a project if it has no 'Tasks' and 'Isuues'. Cascade unlink
        the mail alias related.
        """
        for record in self:
            aliases = record._get_alias()
            record_aux = record
            result = super(project_project, record).unlink()
            if aliases:
                for alias_id in aliases:
                    record_aux._unlink_alias(alias_id.id)
        return result
