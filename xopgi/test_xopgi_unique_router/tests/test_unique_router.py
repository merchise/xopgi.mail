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

from xoeuf.odoo.tests.common import TransactionCase
from xoeuf import api
import email
from xoeuf.odoo.addons.xopgi_mail_threads.stdroutes import BOUNCE_ROUTE_MODEL

NEW_MESSAGE = '''\
From: = User <user@gmail.com>
Message-Id: 0
Subject: New deal
To: <admin@example.com>

This is the message data.
'''

REPLY = '''\
From: User <user@gmail.com>
Subject: Reply
Message-Id: 1
To: <catchall+{thread_index}@example.com>

This is the message data.
'''

REPLY_INVALID_ADDRESS = '''\
From: User <user@gmail.com>
Subject: Reply
Message-Id: 1
To: <catchall+impossible-thread-index@example.com>

This is the message data.
'''


class TestMailRouter(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestMailRouter, self).setUp()
        MailThread = self.env['mail.thread']
        obj_id = MailThread.message_process(
            'test_xopgi_unique_router.model',
            NEW_MESSAGE
        )
        self.thread = self.env['test_xopgi_unique_router.model'].browse(obj_id)
        self.bounce_sent = False

        def set_bounce_sent(value):
            self.bounce_sent = value

        @api.model
        def _check_bounce_sent(self, message, *args, **kwargs):
            MailThread = self.env['mail.thread']
            msg_txt = email.message_from_string(REPLY_INVALID_ADDRESS)
            msg = MailThread.message_parse(msg_txt)
            set_bounce_sent(
                message['from'].startswith('MAILER-DAEMON') and
                message['to'] == msg.get('from') and
                message['subject'].startswith('Re:') and
                message['subject'].endswith(msg.get('subject'))
            )
            return _check_bounce_sent.origin(self, message, *args, **kwargs)

        self._unpatch_send_email()
        self.env['ir.mail_server']._patch_method(
            'send_email',
            _check_bounce_sent
        )

    def tearDown(self):
        super(TestMailRouter, self).tearDown()

    def _unpatch_send_email(self):
        # The pair of methods _patch_method and _revert_method are
        # ill-defined.  In this case: the tests of the addon 'mail' patch the
        # ir.mail_server, and revert, this causes the Model Class to be
        # modified with by setting the 'origin' code of in the Model Class.
        # The Model Class should be empty: so we simply remove the send_email
        # method and allow the MRO to execute smoothly.
        try:
            del type(self.env['ir.mail_server']).mro()[0].send_email
        except:  # noqa
            pass

    def test_unique_address_router(self):
        reply = REPLY.format(thread_index=self.thread.thread_index)
        MailThread = self.env['mail.thread']
        thread_id = MailThread.message_process(
            'test_xopgi_unique_router.model',
            reply
        )
        self.assertEqual(self.thread.id, thread_id)

    def test_no_route_found_generates_bounce(self):
        MailThread = self.env['mail.thread']
        thread_id = MailThread.message_process(
            'test_xopgi_unique_router.model',
            REPLY_INVALID_ADDRESS
        )
        thread_found = self.env[BOUNCE_ROUTE_MODEL].browse(thread_id)
        self.assert_(self.bounce_sent and thread_found)
