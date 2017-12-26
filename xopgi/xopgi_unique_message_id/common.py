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
import re

CATCHALL_DOMAIN = 'mail.catchall.domain'


def encode_message_id(self, message_id):
    domain = self.env['ir.config_parameter'].get_param(CATCHALL_DOMAIN, '')
    seq = self.env['ir.sequence'].get('mail.message.id.seq')
    return "<%s-%s+%s>" % (seq, domain, message_id.strip('<>'))


def decode_message_id(self, message_id):
    return message_id_is_encoded(self, message_id) or message_id


def message_id_is_encoded(self, message_id):
    domain = self.env['ir.config_parameter'].get_param(CATCHALL_DOMAIN, '')
    message_id_re = re.compile(r'(\d+)-%s\+([^@]+)?' % re.escape(domain),
                               re.UNICODE)
    match = message_id_re.search(message_id.strip('<>'))
    if match:
        _, original_part = message_id.split('+', 1)
        return '<%s' % original_part
    return False
