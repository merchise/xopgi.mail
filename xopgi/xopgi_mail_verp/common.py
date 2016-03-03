#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# common
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-16

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.release import version_info as ODOO_VERSION_INFO


# The name of the configuration parameter where the alias for bounces should
# be located.
MAIL_BOUNCE_ALIAS_PARAM = 'mail.bounce.alias'

# The name of the preferred alias for VERP bounces.  If this alias is set the
# 'mail.bounces.alias' won't be used.  This allows to bypass the Odoo
# mail.mail default Return-Path, though VERP is not installed.
MAIL_BOUNCE_VERP_ALIAS_PARAM = 'mail.bounce.verp.alias'

# The default alias.
DEFAULT_BOUNCE_ALIAS = 'postmaster-odoo'

# The name of the internal model to deal with bounces received by Odoo.  This
# is rather internal stuff.
BOUNCE_MODEL = 'mail.bounce.model'

# A void email address should as the argument to a MAIL FROM when bouncing a
# message.  This is such void address.
VOID_EMAIL_ADDRESS = '<>'


def get_bounce_alias(pool, cr, uid, context=None):
    '''Return the alias for building bouncing addresses.

    If no alias are set, return 'postmaster-odoo'.

    '''
    alias_name = ('mail.catchall.alias'
                  if ODOO_VERSION_INFO < (8, 0)
                  else MAIL_BOUNCE_ALIAS_PARAM)
    get_param = pool['ir.config_parameter'].get_param
    bounce = get_param(cr, uid, alias_name,
                       default=DEFAULT_BOUNCE_ALIAS, context=context)
    res = get_param(cr, uid, MAIL_BOUNCE_VERP_ALIAS_PARAM, default=bounce,
                    context=context)
    return res


def valid_email(name, email):
    try:
        return '@' in email
    except:
        return False


def get_recipients(message, include_cc=False):
    'Return the list of (name, email) of the message recipients.'
    # TODO: use openerp.tools.email_split(text)
    from email.utils import getaddresses
    from openerp.addons.mail.mail_thread import decode_header
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
