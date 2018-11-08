#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Probe for ahabana.co.cu rogue bounces.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import email
import re
from xoeuf.odoo.addons.xopgi_mail_threads.utils import get_recipients
from ...common import get_message_walk, find_part_in_walk

MULTIPLE_SPACES = (re.compile(r'[ ]*:'))

NO_REPLY_ADDRESS = (
    re.compile(r'(.*)(noreply@)((?<=[@])ahabana\.co\.cu>?)$')
)


class AHabanaProbe(object):
    '''Test if this is a rogue bounce from ahabana.co.cu.

    This probe is designed for bounces coming from ahabana.co.cu that don't
    follow RFC descriptions for automatic responses.

    No standard bounces patterns are found on this messages. So, only three
    tests are used:

    Tests:

    - The Reply-To contains noreply@ahabana.co.cu.
        Assuming that automatic responses usually use a 'noreply' address as
        reply-to path because there is no interest of receiving an answer.
    - The X-Actual-From contains MDaemon
        Assuming that this particular field is used for automatic responses
        sent by Mailer Daemon.
    - Subject contains notification of no delivery.
        This may change but this is a rogue bounce after all.

    '''
    def __call__(self, msg):
        if not NO_REPLY_ADDRESS.match(msg.get('Reply-To', '')):
            return None
        if 'MDaemon' not in msg.get('X-Actual-From', ''):
            return None
        if 'Your message can not be delivered' not in msg['Subject']:
            return None
        # Get the body of the message, there resides the minimal original
        # message data. With that info it can be known the recipient that is
        # failing.
        walk = get_message_walk(msg)
        part = find_part_in_walk(walk, 'text/plain')
        body = part.get_payload(decode=True)
        failure_parts = body.split('\n\n')
        failure_email = email.message_from_string(MULTIPLE_SPACES.sub(':', failure_parts[1]))
        failures = {email
                    for _, email in get_recipients(failure_email)
                    if email}
        if not failures:
            return None
        result = {'failures': failures}
        receiver = msg['To']
        thread_index = receiver[receiver.find('+') + 1:receiver.find('@')]
        if thread_index:
            result['thread_index'] = thread_index
            return result
        else:
            return None
