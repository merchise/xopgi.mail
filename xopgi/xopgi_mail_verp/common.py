#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from email.utils import getaddresses

from xoeuf.odoo.addons.xopgi_mail_threads.utils import decode_header


# The name configuration parameter for VERP bounces.  Don't use the
# 'mail.bounce.alias' to avoid clashes with Odoo 10.  Odoo 8 didn't have the
# 'mail.bounce.alias' and it won't be missed.
MAIL_BOUNCE_VERP_ALIAS_PARAM = 'xopgi.mail.bounce.verp.alias'

# The default alias.
DEFAULT_BOUNCE_ALIAS = 'postmaster-odoo'

# The name of the internal model to deal with bounces received by Odoo.  This
# is rather internal stuff.
BOUNCE_MODEL = 'mail.bounce.model'

# A void email address should as the argument to a MAIL FROM when bouncing a
# message.  This is such void address.
VOID_EMAIL_ADDRESS = '<>'


def get_bounce_alias(self):
    '''Return the alias for building bouncing addresses.

    If no alias are set, return 'postmaster-odoo'.

    '''
    get_param = self.env['ir.config_parameter'].get_param
    res = get_param(MAIL_BOUNCE_VERP_ALIAS_PARAM, default=DEFAULT_BOUNCE_ALIAS)
    return res


def valid_email(name, email):
    try:
        return '@' in email
    except Exception:
        return False


def get_recipients(message, include_cc=False):
    'Return the list of (name, email) of the message recipients.'
    # TODO: use openerp.tools.email_split(text)
    raw_recipients = [decode_header(message, 'To')]
    if include_cc:
        raw_recipients.append(decode_header(message, 'Cc'))
    recipients = [
        addr for addr in getaddresses(raw_recipients)
        if valid_email(*addr)
    ]
    return recipients


def is_void_return_path(return_path):
    'Indicates if this a bouncy Return-Path.'
    res = not return_path or return_path == VOID_EMAIL_ADDRESS
    if not res:
        # Some MTAs place "<MAILER-DAEMON>" return path upon delivery.
        res = not valid_email('', return_path[1:-1])
    return res


def has_void_return_path(msg, missing_is_void=True):
    return_path = msg['Return-Path']
    if return_path:
        return is_void_return_path(return_path)
    else:
        return missing_is_void


def is_dsn(msg):
    return msg.get_content_type() == 'multipart/report'
