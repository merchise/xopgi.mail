# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_url_attachments.mail_thread
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-23

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from lxml import etree
from openerp import api, models
from openerp.addons.mail.mail_thread import mail_thread as _base_mail_thread
from xoeuf.osv.orm import get_modelname
from six import integer_types, string_types


mail_thread_model = get_modelname(_base_mail_thread)


class MailThread(models.AbstractModel):
    _name = mail_thread_model
    _inherit = _name

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None,
                     type='notification', subtype=None, parent_id=False,
                     attachments=None, context=None, content_subtype='html',
                     **kwargs):
        ''' Find links on body and add its as url attachment con thread.

        '''
        msg_id = super(MailThread, self).message_post(
            cr, uid, thread_id, body=body, subject=subject, type=type,
            subtype=subtype, parent_id=parent_id, attachments=attachments,
            context=context, content_subtype=content_subtype, **kwargs)
        if not body:
            return msg_id
        links = etree.HTML(body).xpath('descendant-or-self::a')
        if not links:
            return msg_id
        thread_model = (self._name
                        if self._name != mail_thread_model
                        else context.get('thread_model', mail_thread_model))
        attachment = self.pool['ir.attachment'].browse(cr, uid, [],
                                                       context=context)
        values = dict(
            res_model=thread_model,
            res_id=(thread_id
                    if isinstance(thread_id, (integer_types, string_types))
                    else thread_id[0]),
            type='url'
        )
        for a in links:
            url = a.attrib.get('href', '')
            name = a.text or url
            if not url.upper().startswith('MAILTO:'):
                values.update(url=url, name=name)
                if not attachment.search_count([(f, '=', v)
                                                for f, v in values.items()
                                                if f != 'name']):
                    attachment.create(values)
        return msg_id
