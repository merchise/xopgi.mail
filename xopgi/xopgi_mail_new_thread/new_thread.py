#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# new_thread
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


FIELD_NAME = 'can_new_thread'
ADD_CANMOVE_TO_READ = object()


class MessagesNewThread(models.Model):
    _inherit = 'mail.message'
    can_new_thread = fields.Boolean(compute='_get_can_new', string='Can New')

    @api.multi
    def _get_can_new(self):
        for record in self:
            has_group = self.env['res.users'].has_group(
                'xopgi_mail_new_thread.group_new_thread'
            )
            type = get_first_of(record, 'type', 'message_type')
            record.can_new_thread = (
                type not in ('notification',) and
                (self._uid == SUPERUSER_ID or has_group))

    @api.model
    def _message_read_dict(self, msg, parent_id=False):
        """ Return a dict representation of the message.
        """
        res = super(MessagesNewThread, self)._message_read_dict(msg, parent_id=parent_id)
        res[FIELD_NAME] = getattr(msg, FIELD_NAME)
        return res

    @api.multi
    def message_format(self):
        with context(ADD_CANMOVE_TO_READ):
            return super(MessagesNewThread, self).message_format()

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        if ADD_CANMOVE_TO_READ in context:
            fields.append(FIELD_NAME)
        return super(MessagesNewThread, self).read(fields=fields, load=load)
