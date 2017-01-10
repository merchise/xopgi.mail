# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xhg_ca_coordination_board.reports.confirmation_time
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2016-07-05

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, fields, models


class MailGroup(models.Model):
    _inherit = 'mail.group'

    enable_auto_subscribe = fields.Boolean(
        default=False,
        string='Enable automatic subscription',
        help='If checked, this group will auto subscribe mail senders'
    )

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None,
                     type='notification', subtype=None, parent_id=False,
                     attachments=None, context=None, content_subtype='html',
                     **kwargs):

        group = self.browse(cr, uid, thread_id, context=context)

        if not group.enable_auto_subscribe:
            if not context:
                context = {}
            context['mail_create_nosubscribe'] = True
            context['mail_post_autofollow'] = False

        return super(MailGroup, self).message_post(cr, uid, thread_id, body,
                                                   subject, type, subtype,
                                                   parent_id, attachments,
                                                   context, content_subtype,
                                                   **kwargs)
