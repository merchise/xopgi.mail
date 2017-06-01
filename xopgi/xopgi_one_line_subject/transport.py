# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_one_line_subject.router
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
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

try:
    from odoo.addons.xopgi_mail_threads import MailTransportRouter
    from odoo.addons.xopgi_mail_threads import TransportRouteData
    from odoo.addons.xopgi_mail_threads.utils \
        import decode_smtp_header as decode
except ImportError:
    from openerp.addons.xopgi_mail_threads import MailTransportRouter
    from openerp.addons.xopgi_mail_threads import TransportRouteData
    from openerp.addons.xopgi_mail_threads.utils \
        import decode_smtp_header as decode


class OneLineSubjectTransport(MailTransportRouter):
    'A MailTransport for ensure subject with only one line.'
    @classmethod
    def query(self, *args, **kwargs):
        return True, None

    def prepare_message(self, obj, message, data=None):
        '''Remove new line character from message subject.

        '''
        subject = decode(message['subject'])
        # Remove new line character.
        subject = decode(subject.replace('\n', ' '))
        del message['subject']  # Ensure a single subject
        message['subject'] = subject
        return TransportRouteData(message, {})
