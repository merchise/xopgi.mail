# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_move_copy_msg_commons
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-02-13

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, models
from xoeuf.osv.orm import REPLACEWITH_RELATED


def get_model_selection(self):
    """Get message_capable_models with at least one thread.

    """
    thread_obj = self.env['mail.thread']

    def check(model):
        try:
            return self.env[model].search([], limit=1, count=True)
        except:
            return False

    def translate(source):
        translation = self.env['ir.translation'].sudo()
        return translation._get_source(None, ('model',),
                                       self._context.get('lang', False),
                                       source) or source
    model_names = [(n, translate(d)) for n, d in
                   thread_obj.message_capable_models().items() if
                   (n != 'mail.thread' and check(n))]
    return model_names


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def do_move_message(self, model, res_id, leave_msg=True):
        new_msg = self.env['mail.message']
        parent_id = self.search(
            [('res_id', '=', res_id), ('model', '=', model),
             ('parent_id', '=', False)], limit=1).id
        msg_values = dict(model=model, res_id=res_id, parent_id=parent_id)
        att_values = dict(res_model=model, res_id=res_id)
        record_name = self._get_record_name(msg_values)
        msg_values.update(record_name=record_name)
        if leave_msg:
            for msg in self:
                ids = [att.copy(dict(att_values, name=att.name)).id for att in
                       msg.attachment_ids]
                new_msg += msg.copy(dict(
                    msg_values, attachment_ids=[REPLACEWITH_RELATED(*ids)]))
        else:
            new_msg = self
            new_msg.write(msg_values)
            for msg in self:
                if msg.attachment_ids:
                    msg.attachment_ids.write(att_values)
        notify = lambda _id: self._model._notify(self._cr, self._uid, _id,
                                                 context=self._context)
        for item in new_msg:
            notify(item.id)
