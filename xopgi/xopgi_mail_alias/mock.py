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


from xoutil.symbols import Unset

from xoeuf import api, models, fields
from xoeuf.odoo import _
from xoeuf.odoo.exceptions import ValidationError
from xoeuf.odoo.tools.safe_eval import safe_eval

from .mail_alias import get_default_alias_domain


class AliasMockerMixin(models.AbstractModel):
    '''A mixin that mocks mail.alias.

    True implementations will always read the data from the 'mail.alias'
    model.  A virtual mail alias is simply made available so that other parts
    of the systems (views, most importantly) are easily made.

    A virtual alias is by all means a 'mail.alias' that gains other attributes
    via the 'alias_defaults' dictionary.

    Proposed usage::

        >>> class project_valias(models.Model):
        ... _auto = False
        ... _name = 'project.valias'
        ... _inherit = ['xopgi.mail.alias.mocker']
        ...
        ... project_id = fields.Many2one('project.project', string='Project')

    Then the 'project_id' attribute of 'project.valias' will be the key
    'project_id' in the 'alias_default' attribute of any 'mail_alias'.

    '''
    _name = 'xopgi.mail.alias.mocker'

    alias_name = fields.Char(
        'Alias',
        required=True,
        help=("The name of the email alias, e.g. 'jobs' if "
              "you want to catch emails "
              "for <jobs@example.my.openerp.com>")
    )

    alias_domain = fields.Char(
        'Domain',
        required=True,
        default=get_default_alias_domain,
        help=("The domain of the email alias, e.g. "
              "'example.my.openerp.com' if you want to catch emails "
              "for <jobs@example.my.openerp.com>")
    )

    alias_defaults = fields.Text(
        'Default Values',
        default='{}',
        help=("A Python dictionary that will be evaluated to "
              "provide default values when creating new "
              "records for this alias.")
    )

    alias_force_thread_id = fields.Integer(
        'Record Thread ID',
        help=("Optional ID of a thread (record) to which "
              "all incoming messages will be attached, "
              "even if they did not reply to it. If set, "
              "this will disable the creation of new "
              "records completely.")
    )

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """Read the ids from mail.alias if any of fields are not present on
        mail.alias model then search it on alias_defaults dict.

        """
        Model = self.env['mail.alias']
        extraneous = []
        for field in fields:
            if field not in Model._fields.keys():
                extraneous.append(field)
        if extraneous:
            fields = list(set(fields) - set(extraneous))
        if extraneous and 'alias_defaults' not in fields:
            default_added = True
            fields.append('alias_defaults')
        else:
            default_added = False
        result = Model.browse(self.ids).read(fields)
        if not extraneous:
            return result
        else:
            for row in result:
                defaults = str2dict(row['alias_defaults'])
                for field in extraneous:
                    row[field] = defaults.pop(field, False)
                # Restore the defaults but it will have only the keys not
                # in 'extraneous' (those upgraded to fields)
                if not default_added:
                    row['alias_defaults'] = repr(defaults)
                else:
                    row.pop('alias_defaults')
        return result

    @api.model
    def _parse_fields(self, alias_id, vals):
        '''The fields not present on mail.alias model are include on
           alias_defaults dictionary.
        '''
        Aliases = self.env['mail.alias']
        extraneous = []
        fields = set(vals.keys())
        for field in vals.keys():
            if field not in Aliases._fields.keys():
                extraneous.append(field)
        if extraneous:
            fields -= set(extraneous)
            defaults = {}
            if 'alias_defaults' in fields:
                defaults = str2dict(vals['alias_defaults'], 'Default Values')
            else:
                if alias_id:
                    record = Aliases.browse(alias_id)
                    row = record.read(['alias_defaults'])
                    defaults = str2dict(row[0]['alias_defaults'], 'Default Values')
            for field in extraneous:
                value = vals.pop(field, False)
                if field in defaults:
                    defaults.update({field: value})
                else:
                    defaults.setdefault(field, value)
            vals['alias_defaults'] = repr(defaults)
        return vals


def str2dict(maybedict, field_name=None, default=Unset):
    from collections import Mapping
    from xoutil.eight import string_types
    try:
        if isinstance(maybedict, Mapping):
            return dict(maybedict)
        elif isinstance(maybedict, string_types):
            return dict(safe_eval(maybedict))
        elif default is not Unset:
            return default
        else:
            raise TypeError
    except(ValueError, TypeError):
        raise ValidationError(
            _("The format's field '%s' is incorrect because not have "
              "structure dictionary. "
              "Example: {'field1': value1, 'field2': value2}") % field_name
        )
