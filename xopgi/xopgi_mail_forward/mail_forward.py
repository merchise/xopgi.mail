#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print)

from lxml import html
from xoutil.string import cut_prefixes

from xoeuf import models, api
from xoeuf.odoo.tools.translate import _


# We need the first two empty paragraph so that the cursor goes there.  Also
# the new-line chars in this text will allow for the trick in JS converting an
# HTML to text to format nicely.
MAIL_BODY_TEMPLATE = '''
<p></p><p></p>
<p><i>----------Original message----------</i></p>
<p>Subject: %(subject)s <br/>
From: %(author)s <br/>
To: %(partners)s <br/>
Date: %(date)s <br/></p>

%(body)s
'''


class ForwardMail(models.TransientModel):
    """Allow forwarding a message.

    It duplicates the message and optionally attaches it to another object of
    the database and sends it to another recipients than the original one.

    """
    _name = 'mail.compose.message'
    _inherit = _name

    @api.model
    def get_forward_action(self, message_id):
        message = self.env['mail.message'].browse(message_id)
        get_partner = lambda follower: follower.partner_id
        thread = self.env[message.model].browse(message.res_id)
        partners = thread.message_follower_ids.mapped(get_partner)
        partner_list = [
            partner.name
            for partner in partners
            if partner and partner.name
        ]
        body = MAIL_BODY_TEMPLATE % dict(
            subject=message.subject,
            author=message.author_id.name,
            partners=', '.join(partner_list),
            date=message.date,
            body=message.body
        )
        context = dict(
            default_body=body,
            default_model=message.model,
            default_res_id=message.res_id,
            default_subject=("Fwd: %s" % message.record_name),
            mail_post_autofollow=True
        )
        return dict(
            type='ir.actions.act_window',
            res_model='mail.compose.message',
            view_mode='form',
            view_type='form',
            views=[[False, 'form']],
            target='new',
            context=context
        )

    @api.model
    def default_get(self, fields):
        result = super(ForwardMail, self).default_get(fields)
        result['subject'] = (
            self._context.get('default_subject') or result.get('subject')
        )
        # Fix unclosed HTML tags.
        body = result.get('body', '')
        if body.strip():
            result['body'] = html.tostring(html.document_fromstring(body))
        model = self._context.get('default_model', None)
        res_id = self._context.get('default_res_id')
        if model and res_id:
            name = self.env[model].browse(int(res_id)).name_get()[0][1]
            result['record_name'] = name
            if not result['subject']:
                result['subject'] = _('Fwd:') + cut_prefixes(
                    name, _('Re:'), _('Fwd:')
                )
        return result
