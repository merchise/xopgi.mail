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
import logging

from xoeuf.odoo.addons.xopgi_mail_threads.utils import get_recipients

logger = logging.getLogger(__name__)
del logging

MULTIPLE_SPACES = re.compile(r'[ \t]*:')
NO_REPLY_ADDRESS = re.compile(r'.*noreply@ahabana\.co\.cu>?$')
THREAD_REGEXP = re.compile(r'\+(?P<index>[a-z0-9]+)@[^@]+$')


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
        # We need to inspect the body of the message, to get the failing
        # (bouncing) address.  The message is formatted "like" an email with
        # extra spaces in the headers; see the file rogue-ahabana.eml in the
        # tests.
        #
        # We use a little trick: parse the body as an email (RFC 2822) to the
        # all the recipients.
        body = msg.get_payload(decode=True)
        chunks = body.split('\n\n')
        failing_email = email.message_from_string(
            # The 2nd chunk contains the "header-like message".
            MULTIPLE_SPACES.sub(':', chunks[1])
        )
        failures = {
            email
            for _, email in get_recipients(failing_email)
            if email
        }
        if not failures:
            logger.error(
                'Message %s detected as rogue bounce, but unable to detect '
                'failing addresses',
                msg['Message-Id'],
                extra=dict(body=body)
            )
            return None
        result = {'failures': failures}
        thread_match = THREAD_REGEXP.search(msg.get('To', ''))
        if thread_match:
            result['thread_index'] = thread_match.groupdict()['index']
            return result
        else:
            # TODO: Here we should discard the message instead of letting
            # going throu.  It's a bounce; but we can locate the thread.
            return None
