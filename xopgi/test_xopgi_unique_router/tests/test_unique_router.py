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
        obj_id = MailThread.message_process('test_router.model', FIRST)
        mail_msg = self.env['mail.message'].search([('res_id', '=', obj_id)])
        self.obj = mail_msg[0]

    def tearDown(self):
        super(TestMailRouter, self).tearDown()

    def test_unique_address_router(self):
        reply = REPLY.format(thread_index=self.obj.thread_index)
        MailThread = self.env['mail.thread']
        thread_id = MailThread.message_process(
            'test_router.model',
            reply
        )
        self.assertEqual(self.obj.res_id, thread_id)

    def test_no_route_found_generates_bounce(self):
        MailThread = self.env['mail.thread']
        thread_id = MailThread.message_process(
            'test_router.model',
            REPLY_INVALID_ADDRESS
        )
        self.failIf(thread_id)
