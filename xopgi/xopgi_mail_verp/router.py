# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.router
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
A MailRouter for bounced messages.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import re

from openerp.release import version_info as ODOO_VERSION_INFO
from openerp.addons.xopgi_mail_threads import MailRouter
from openerp.addons.mail.mail_thread import decode_header

from .mail_bounce_model import BOUNCE_MODEL

from xoutil import logger as _logger


class BouncedMailRouter(MailRouter):
    @classmethod
    def _message_route_check_bounce(self, cr, uid, message):
        """ Verify that the email_to is the bounce alias. If it is the
        case, log the bounce, return the origin route. """
        from xoeuf.osv.registry import Registry
        from .common import get_bounce_alias
        registry = Registry(cr.dbname)
        bounce_alias = get_bounce_alias(registry, cr, uid)
        message_id = message.get('Message-Id')
        email_from = decode_header(message, 'From')
        email_to = decode_header(message, 'To')
        if bounce_alias not in email_to:
            return None
        # Bounce regex
        # Typical form of bounce is bounce_alias-128-crm.lead-34@domain
        # group(1) = the mail ID; group(2) = the model (if any);
        # group(3) = the record ID
        bounce_re = re.compile(
            ("%s-(\d+)-?([\w.]+)?-?(\d+)?" % re.escape(bounce_alias)),
            re.UNICODE)
        bounce_match = bounce_re.search(email_to)
        if bounce_match:
            bounced_mail_id = bounce_match.group(1)
            bounced_model = bounce_match.group(2) or None
            bounced_thread_id = bounce_match.group(3) or False
            _logger.info(
                'Routing mail from %s to %s with Message-Id %s: '
                'bounced mail from mail %s, model: %s, thread_id: %s',
                email_from, email_to, message_id, bounced_mail_id,
                bounced_model, bounced_thread_id)
            thread_id = (bounced_mail_id, bounced_model, bounced_thread_id)
            if ODOO_VERSION_INFO < (8, 0):
                return (BOUNCE_MODEL, thread_id, {}, uid)
            else:
                return (BOUNCE_MODEL, thread_id, {}, uid, None)

    @classmethod
    def is_applicable(cls, cr, uid, message):
        return bool(cls._message_route_check_bounce(cr, uid, message))

    @classmethod
    def apply(cls, cr, uid, routes, message):
        route = cls._message_route_check_bounce(cr, uid, message)
        if route:
            # We assume a bounce should never create anything else.  What's
            # the point for creating a lead, or task... Specially if the alias
            # is bound to some ids.  This only could happen if another router
            # is in place and that would be a design error.
            routes[:] = [route]
        return routes
