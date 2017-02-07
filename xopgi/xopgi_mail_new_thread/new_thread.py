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


from openerp import SUPERUSER_ID
from openerp.osv import osv, fields


FIELD_NAME = 'can_new_thread'


class Message(osv.Model):
    _inherit = 'mail.message'

    def _get_can_new(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        has_group = self.pool['res.users'].has_group(
            cr, uid, 'xopgi_mail_new_thread.group_new_thread')
        for msg in self.browse(cr, uid, ids, context=context):
            result[msg.id] = (msg.type != 'notification' and
                              (uid == SUPERUSER_ID or has_group))
        return result

    _columns = {
        FIELD_NAME:
            fields.function(_get_can_new, string='Can New',
                            type='boolean'),
    }

    def _message_read_dict(self, cr, uid, msg, parent_id=False,
                           context=None):
        res = super(Message, self)._message_read_dict(
            cr, uid, msg, parent_id=parent_id, context=context)
        res[FIELD_NAME] = msg.can_new_thread
        return res
