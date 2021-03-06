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

from xoeuf import api, fields, models
from xoeuf.osv.orm import REPLACEWITH_RELATED


def get_model_selection(self):
    """Get message_capable_models with at least one thread.

    """
    thread_obj = self.env['mail.thread']
    translation = self.env['ir.translation'].sudo()

    def translate(source):
        return translation._get_source(None, ('model',),
                                       self._context.get('lang', False),
                                       source) or source
    model_names = [(n, translate(d))
                   for n, d in thread_obj.message_capable_models().items()
                   if n != 'mail.thread']
    return model_names


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def do_move_message(self, model, res_id, leave_msg=True):
        new_msg = self.env['mail.message']
        parent_id = self.search(
            [('res_id', '=', res_id), ('model', '=', model),
             ('parent_id', '=', False)],
            limit=1
        ).id
        msg_values = dict(model=model, res_id=res_id, parent_id=parent_id)
        att_values = dict(res_model=model, res_id=res_id)
        record_name = self._get_record_name(msg_values)
        msg_values.update(record_name=record_name)
        if leave_msg:
            for msg in self:
                ids = [
                    att.copy(dict(att_values, name=att.name)).id
                    for att in msg.attachment_ids
                ]
                new_msg += msg.copy(dict(
                    msg_values,
                    attachment_ids=[REPLACEWITH_RELATED(*ids)]
                ))
        else:
            new_msg = self
            new_msg.write(msg_values)
            for msg in self:
                if msg.attachment_ids:
                    msg.attachment_ids.write(att_values)
        for item in new_msg:
            self._notify(item.id)


class CommonThreadWizard(models.TransientModel):
    _name = 'common.thread.wizard'

    model_id = fields.Selection(
        string='Model', selection=lambda self: get_model_selection(self),
        required=True)
    view = fields.Many2one('xopgi.selectable.view')
    views_count = fields.Integer(compute='_get_views_count')

    @api.onchange('model_id')
    @api.depends('model_id')
    def _get_views_count(self):
        selectable_view = self.env['xopgi.selectable.view']
        for wizard in self:
            if wizard.model_id:
                conf_views = selectable_view.get_views(self.model_id)
                views_count = len(conf_views)
                self.views_count = views_count
                if views_count >= 1:
                    self.view = conf_views[0]
            else:
                self.views_count = 0
                self.view = False

    def get_thread_action(self, res_id=None):
        """ Returns the action that shows the form of this model
        """
        return self.view.get_action(model=self.model_id, res_id=res_id)


class SelectableView(models.Model):
    _name = 'xopgi.selectable.view'
    _rec_name = 'label'
    _order = 'priority'

    label = fields.Char(translate=True, required=True)
    model_id = fields.Selection(
        string='Model', selection=lambda self: get_model_selection(self),
        required=True)
    view = fields.Many2one('ir.ui.view', required=True)
    priority = fields.Integer(default=16)

    def get_views(self, model):
        domain = [('model_id', '=', model)]
        return self.search(domain)

    def get_action(self, model=None, target='current', res_id='None'):
        """ Return an ir.actions.act_window
        """
        res = dict(target=target)
        if self:
            view = self[0]
            model = view.model_id

        if res_id is not None:
            # If the recordset is empty in Odoo8 it returns an empty list.In
            # odoo10 gives error.
            values_action = self.env[model].browse(res_id).get_access_action()

            # If values_action contains a list it is because get_acess_action
            # was executed #in odoo8 and returns a [{}], in odoo10 returns a {}.
            if isinstance(values_action, list):
                values_action = values_action[0]
            res = dict(values_action, **res)
        else:
            values = {
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(self.view.id, 'form')],
                'context': self._context
            }
            res = dict(values, **res)
        return res

    @api.multi
    def try_selected_view(self):
        return self.get_action(target='new')
