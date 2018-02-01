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

from xoeuf import api, models, fields, MAJOR_ODOO_VERSION
from xoeuf.odoo import _
from xoeuf.odoo.exceptions import Warning as UserError
from xoeuf.osv.orm import CREATE_RELATED, UPDATE_RELATED, REMOVE_RELATED


if MAJOR_ODOO_VERSION < 9:
    TEAM_ID_NAME = 'section_id'
    TEAM_MODEL_NAME = 'crm.case.section'
else:
    TEAM_ID_NAME = 'team_id'
    TEAM_MODEL_NAME = 'crm.team'


class crm_valias(models.Model):
    _name = 'crm.valias'
    _inherit = ['xopgi.mail.alias.mocker']

    type = fields.Selection(
        [('lead', 'Lead'),
         ('opportunity', 'Opportunity')],
        'Type',
        index=True,
        help="Type of object to create by incoming messages."
    )

    if MAJOR_ODOO_VERSION < 9:
        section_id = fields.Many2one(TEAM_MODEL_NAME, string='Sale Team')
    else:
        team_id = fields.Many2one(TEAM_MODEL_NAME, string='Sale Team')

    user_id = fields.Many2one('res.users', string='Team Leader')


class crm_case_section(models.Model):
    _inherit = TEAM_MODEL_NAME

    @api.model
    def _get_model_id(self):
        model_obj = self.env['ir.model']
        return model_obj.search([('model', '=', 'crm.lead')]).id

    @api.multi
    def _get_alias(self):
        """Returns aliases related to a sale_team.
        """
        Alias = self.env['mail.alias']
        Virtual = self.env['crm.valias']
        model_id = self._get_model_id()
        for record in self:
            aliases = Alias.search([('alias_model_id', '=', model_id)])\
                           .filtered(lambda a: eval(a.alias_defaults).get(TEAM_ID_NAME, 0) == record.id)\
                           .mapped('id')
            record.alias_ids = Virtual.browse(aliases)

    @api.multi
    def _unlink_alias(self, alias_id):
        Alias = self.env['mail.alias']
        section_ids = self.search([('alias_id', '=', alias_id),
                                   ('active', '=', False),
                                   ('id', '!=', self.id)])
        if section_ids:
            section_ids.unlink()
        return Alias.browse(alias_id).unlink()

    def validate_type_alias(self, vals, use_lead, use_opportunity):
        alias = eval(vals['alias_defaults'])
        type_valias = alias.get('type', False)
        if not type_valias:
            return vals
        if use_lead is None:
            use_lead = self.use_leads
        if use_opportunity is None:
            use_opportunity = self.use_opportunities
        if not use_lead and type_valias == 'lead':
            raise UserError(_(
                "This sale team not use 'Leads' then cant alias with "
                "'Lead'.  Please select the 'Leads' option from "
                "'Sales team'"
            ))
        if not use_opportunity and type_valias == 'opportunity':
            raise UserError(_(
                "This sale team not use 'Opportunities' then cant alias with "
                "'Opportunity' please select the Opportunities' option from "
                "'Sales team'."
            ))
        return vals

    @api.multi
    def _set_alias(self):
        pass

    def set_values(self, field_value, use_lead, use_opportunity):
        """It manages the CRUD of mail aliases for a project. In the case of
        "create" it returns a list of the identifiers of the new mail alias
        that have been created. In the case of write and unlink it returns an
        empty list.
        """
        Alias = self.env['mail.alias']
        Virtual = self.env['crm.valias']
        alias_model_id = self._get_model_id()

        def update_values(id, vals):
            if MAJOR_ODOO_VERSION < 9:
                vals['section_id'] = self.id
            else:
                vals['team_id'] = self.id
            vals['alias_model_id'] = alias_model_id
            vals = Virtual._parse_fields(id, vals)
            vals = self.validate_type_alias(vals, use_lead, use_opportunity)
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
        'crm.valias',
        compute='_get_alias',
        inverse='_set_alias',
        string='Mail Aliases',
        help=("The email addresses associated with this team. New emails "
              "received will automatically create new Lead/Opportunity "
              "assigned to the team.")
    )

    @api.model
    def create(self, values):
        """Odoo create by default a mail alias.This function allows you to
           create more than one mail alias since a project is created for the
           first time.
        """
        from xoutil.string import normalize_slug
        if not values.get('alias_name'):
            values['alias_name'] = normalize_slug(values['name'])
            Alias = self.env['mail.alias']
            vals = {}
            valias = values.pop('alias_ids', None)
            if valias:
                use_lead = values.get('use_leads', None)
                use_opportunitie = values.get('use_opportunities', None)
                aliases_create = self.set_values(valias, use_lead, use_opportunitie)
            else:
                aliases_create = []
        sale_team = super(crm_case_section, self).create(values)
        if sale_team and aliases_create:
            for alias in aliases_create:
                record = Alias.browse(alias)
                defaults = eval(record.alias_defaults)
                if MAJOR_ODOO_VERSION < 9:
                    defaults.update(section_id=sale_team.id)
                else:
                    # Odoo 9 and 10 changed the section_id to a team_id.
                    defaults.update(team_id=sale_team.id)
                vals['alias_defaults'] = repr(defaults)
                record.write(vals)
        return sale_team

    @api.multi
    def write(self, values):
        """Override the project for to update relation of valias-project
        """
        if 'alias_ids' in values:
            valias = values.pop('alias_ids')
            use_lead = values.get('use_leads', None)
            use_opportunity = values.get('use_opportunities', None)
            self.set_values(valias, use_lead, use_opportunity)
        return super(crm_case_section, self).write(values)

    @api.multi
    def unlink(self):
        """Cascade unlink the mail alias related.
        """
        for record in self:
            aliases = record._get_alias()
            record_aux = record
            result = super(crm_case_section, record).unlink()
            if aliases:
                for alias_id in aliases:
                    record_aux._unlink_alias(alias_id.id)
        return result
