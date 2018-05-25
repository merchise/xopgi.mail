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
from xoeuf import api
from xoeuf.odoo.tests.common import TransactionCase


NEW = '''\
From: traveler_00001@m.evaneos.com
Subject: New proposition
Message-Id: <1>

This is the message data.
'''

REPLY = '''\
From: other_00001_other-stuff@m.evaneos.com
Subject: Reply
Message-Id: <2>

This is the message data
'''


class TestEvaneosRouter(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestEvaneosRouter, self).setUp()
        MailThread = self.env['mail.thread']
        Partner = self.env['res.partner']
        obj_id = MailThread.message_process('test_evaneos.model', NEW)
        self.obj = obj = self.env['test_evaneos.model'].browse(obj_id)
        obj.message_subscribe(Partner.create(dict(
            name='Other Evaneos Address',
            email='other_00001@m.evaneos.com',
        )).ids)
        obj.message_subscribe(Partner.create(dict(
            name='Other Non-Evaneos Address',
            email='user@example.com',
        )).ids)

        self.recipients = recipients = []

        @api.model
        def _collect_recipients(self, message, *args, **kwargs):
            get = message.get_all
            for header in ['To', 'Cc', 'Bcc']:
                recipients.extend(
                    email for _, email in getaddresses(get(header, []))
                )

        self.env['ir.mail_server']._patch_method(
            'send_email',
            _collect_recipients
        )

    def tearDown(self):
        self.env['ir.mail_server']._revert_method('send_email')

    def test_receiving_a_reply_reaches_the_same_object(self):
        MailThread = self.env['mail.thread']
        reply = MailThread.message_process('test_evaneos.model', REPLY)
        self.assertEqual(self.obj, reply)

    def test_receiving_from_evaneos_doesnot_notify_evaneos(self):
        MailThread = self.env['mail.thread']
        MailThread.message_process('test_evaneos.model', REPLY)
        self.assertIn('user@example.com', self.recipients)
        self.assertNotIn('other_00001@m.evaneos.com', self.recipients)
