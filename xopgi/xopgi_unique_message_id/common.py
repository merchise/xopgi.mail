# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.common
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-02

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)
import re

CATCHALL_DOMAIN = 'mail.catchall.domain'


def encode_message_id(self, cr, uid, message_id):
    domain = self.pool['ir.config_parameter'].get_param(
        cr, uid, CATCHALL_DOMAIN)
    seq = self.pool['ir.sequence'].get(cr, uid, 'mail.message.id.seq')
    return "<%s-%s+%s>" % (seq, domain, message_id.strip('<>'))


def decode_message_id(self, cr, uid, message_id):
    return message_id_is_encoded(self, cr, uid, message_id) or message_id


def message_id_is_encoded(self, cr, uid, message_id):
    domain = self.pool['ir.config_parameter'].get_param(
        cr, uid, CATCHALL_DOMAIN)
    message_id_re = re.compile("(\d+)-%s+?([^@]+)?" % re.escape(domain),
                               re.UNICODE)
    match = message_id_re.search(message_id.strip('<>'))
    if match:
        _, original_part = message_id.split('+', 1)
        return '<%s' % original_part
    return False
