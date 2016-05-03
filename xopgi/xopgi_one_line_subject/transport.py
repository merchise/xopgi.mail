# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_one_line_subject.router
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-05-02

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.string import safe_encode

from xoeuf.osv.model_extensions import search_browse

from openerp import SUPERUSER_ID

from openerp.models import Model
from openerp.osv import fields

from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.xopgi_mail_threads import TransportRouteData
try:
    # Odoo 8
    from openerp.addons.mail.mail_message import decode
except ImportError:
    # Odoo 9 fallback
    from openerp.addons.mail.models.mail_message import decode


class OneLineSubjectTransport(MailTransportRouter):
    '''A MailTransport for ensure subject with only one line.

    '''

    @classmethod
    def query(self, *args, **kwargs):
        ''' Always apply.

        '''
        return True, None

    def prepare_message(self, obj, cr, uid, message, data=None, context=None):
        '''Remove new line character from message subject.

        '''
        subject = decode(message['subject'])
        # Remove new line character.
        subject = decode(subject.replace('\n', ' '))
        del message['subject']  # Ensure a single subject
        message['subject'] = subject
        return TransportRouteData(message, {})
