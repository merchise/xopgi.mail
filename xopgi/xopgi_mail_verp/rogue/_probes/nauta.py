#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# nauta
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-03-01

'''Probe for nauta.cu rogue bounces.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


import re
from ...common import has_void_return_path, is_dsn


class NautaProbe(object):
    '''Test if this a rogue from nauta.cu.

    Tests:

    - The Return-Path is a "void" return path.

    - The Content-Type is 'multipart/report; report-type=delivery-status;...'

    - The message contains a 'message/delivery-status' part with
      Reporting-MTA: dns; smtp.nauta.cu

    If there's a message/rfc822 part will see if there's a
    'X-Odoo-Thread-Index' to get the thread's index.  We require that such
    message contains a header whose value is a bounce address.  Such bounce
    address will be used as the 'possible return path'.

    If no possible return path is found this probe will return None.

    '''
    def __call__(self, msg):
        if not has_void_return_path(msg) or not is_dsn(msg):
            return
        walk = self.message_walk(msg)
        report = self.find_part(walk, 'message/delivery-status')
        if not report:
            return None
        # We require the report to contain a Reporting-MTA in the list of know
        # Nauta DNS.  The 'message/delivery-status' contains several parts,
        # the first part is regarding the 'message', the other parts identify
        # the failed recipients.
        message_report = report.get_payload()[0]
        if not self.match_mtas(message_report):
            # Does not match any known MTA for which this probe is valid
            return None
        failures = {address
                    for part in report.get_payload()[1:]
                    for address in self._failed_recipients(part)
                    if address}
        if not failures:
            return None
        result = {'failures': failures}
        # Although the original message is not required by the RFC 1892, we
        # would not be able to find the bounce address without it.
        # Furthermore Nauta (or nauta-like MTAs) do include this in its
        # bounce, so we leverage this.
        original = self.find_part(walk, 'message/rfc822')
        if not original:
            return None
        contents = original.get_payload()
        # The 'message/rfc822' is seen as multipart and, thus, the
        # payload is the message's parts.  There should be a single
        # one with the original message.
        if not original.is_multipart() or not len(contents):
            return None
        message = contents[0]
        index = message['X-Odoo-Thread-Index']
        if index:
            result['thread_index'] = index
            # THIS IS THE ONLY code-path that should return non-None.
            return result
        else:
            return None

    def message_walk(self, msg):
        parts = [msg]
        while parts:
            part = parts.pop(0)
            res = yield part
            if res != 'prune' and part.is_multipart():
                parts.extend(part.get_payload())

    def find_part(self, walk, ctype):
        try:
            part = next(walk)
            while part.get_content_type() != ctype:
                part = next(walk)
            return part
        except StopIteration:
            return None

    def match_mtas(self, msg):
        mta = msg['Reporting-MTA'].lower().strip()
        patterns = list(self._REPORTING_MTA_PATTERNS)
        match = None
        while not match and patterns:
            pattern = patterns.pop(0)
            match = pattern.match(mta)
        return bool(match)

    def _failed_recipients(self, msg):
        if msg['action'] == 'failed':
            recipient = msg['final-recipient']
            if recipient and ';' in recipient:
                _, recipient = recipient.rsplit(';', 1)
                yield recipient.strip()

    _REPORTING_MTA_PATTERNS = (
        re.compile(r'^dns;\s+smtp.nauta.cu$'),
    )
