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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class NewThreadWizard(osv.TransientModel):
    _name = 'new.thread.wizard'

    _columns = {
        'model_id':
            fields.selection(
                lambda s, c, u: s.pool['mail.thread'].message_capable_models(
                    c, u).items(), 'Model', required=True),
        'message_id':
            fields.many2one('mail.message', 'Message', readonly=True),
        'leave_msg':
            fields.boolean('Preserve original message',
                           help="Check for no remove message from original "
                                "thread."),
    }

    _defaults = {
        'leave_msg': True
    }

    def confirm(self, cr, uid, ids, context=None):
        return True
