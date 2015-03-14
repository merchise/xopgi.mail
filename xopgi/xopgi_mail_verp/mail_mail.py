# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.mail_mail
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

'''
Override the send method to add mail_id on context.
'''

from openerp.osv import osv

class mail_mail(osv.Model):
    _name = 'mail.mail'
    _inherit = _name

    def send(self, cr, uid, ids, **kwargs):
        '''
        Add mail_id to context and call _super one by one.

        mail_id may use to get unique return-path.

        '''
        context = kwargs.get('context', {})
        _super = super(mail_mail, self).send
        for _id in ids:
            context.update(mail_id=_id)
            kwargs.update(context=context)
            return _super(cr, uid, [_id], **kwargs)
        return True