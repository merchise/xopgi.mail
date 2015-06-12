# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10
from openerp.osv import osv, fields


class MoveMessageWizard(osv.TransientModel):
    _name = 'move.message.wizard'

    _columns = {
        'thread_id':
            fields.reference('Destination Mail Thread', selection=(
                lambda s, u, c, ctx:
                s.pool['mail.thread'].message_capable_models(
                    c, u, context=ctx).items()), size=128, required=True),
        'message_ids': fields.many2many('mail.message', 'message_move_rel',
                                        'move_id', 'message_id',
                                        'Messages', readonly=True),
        'leave_msg':
            fields.boolean('Preserve original messages',
                           help="Check for no remove message from original "
                                "thread."),
    }

    _defaults = {
        'leave_msg': True
    }
