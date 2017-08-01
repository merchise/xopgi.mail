#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# message_move
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-01-13

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import models, fields, api
from xoeuf.odoo import SUPERUSER_ID

from xoutil.context import context
from xoutil.objects import get_first_of


FIELD_NAME = 'can_move'
ADD_CANMOVE_TO_READ = object()


class Messages(models.Model):
    _inherit = 'mail.message'
    can_move = fields.Boolean(compute='_get_can_move', string='Can New')

    @api.multi
    def _get_can_move(self):
        for record in self:
            has_group = self.env['res.users'].has_group(
                'xopgi_mail_move_message.group_move_message'
            )
            type = get_first_of(record, 'type', 'message_type')
            record.can_move = (
                type not in ('notification', ) and
                (self._uid == SUPERUSER_ID or has_group)
            )

    @api.model
    def _message_read_dict(self, msg, parent_id=False):
        """ Return a dict representation of the message.
        """
        res = super(Messages, self)._message_read_dict(msg, parent_id=parent_id)
        res[FIELD_NAME] = getattr(msg, FIELD_NAME)
        return res

    @api.multi
    def message_format(self):
        with context(ADD_CANMOVE_TO_READ):
            return super(Messages, self).message_format()

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        if ADD_CANMOVE_TO_READ in context:
            fields.append(FIELD_NAME)
        return super(Messages, self).read(fields=fields, load=load)
