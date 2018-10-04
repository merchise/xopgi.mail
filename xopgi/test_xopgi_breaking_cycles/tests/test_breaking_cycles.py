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
from xoeuf.odoo.addons.xopgi_mail_threads.stdroutes import IGNORE_MESSAGE_ROUTE_MODEL
from xoeuf.odoo.addons.xopgi_mail_breaking_cycles.breaker import BreakingCyclesTransport

MESSAGE = '''\
From: = <admin@example.com>
Subject: New deal
To: User <user@example.com>
Message-Id: <1>

This is the message data.
'''

REPLY = '''\
From: = <admin@example.com>
Subject: Reply
To: User <user@example.com>
In-Reply-To: <1>
This is the message data.
'''

FIRST_AUTO_SUBMITTED = '''\
From: = <user@example.com>
Subject: Out of office
Auto-Submitted: auto-replied
In-Reply-To: <1>
To: <bounces+{thread_index}@example.com>

This is the message data.
'''

SECOND_AUTO_SUBMITTED = '''\
From: = <admin@example.com>
Subject: RE: Out of the office
In-Reply-To: <1>
Auto-Submitted: auto-replied
To: <breaking-cycle+{thread_index}@example.com>

This is the message data.
'''


class TestBreakingCycles(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestBreakingCycles, self).setUp()
        MailThread = self.env['mail.thread']
        Partner = self.env['res.partner']
        User = self.env['res.users']
        # Create partner and user for original message sender.  It will be the
        # only notified part when the first auto-submitted message arrived.
        partner_id = Partner.create(dict(
            name='Admin',
            email='admin@example.com',
        )).ids
        User.create({
            'name': 'Admin',
            'login': 'admin_example',
            'email': 'admin@example.com',
            'partner_id': partner_id[0]
        })
        obj_id = MailThread.message_process('test_xopgi_breaking_cycles.model', MESSAGE)
        obj = self.env['test_xopgi_breaking_cycles.model'].browse(obj_id)
        obj.message_subscribe(Partner.create(dict(
            name='Other Address',
            email='other_test@example.com',
        )).ids)
        # Get VERP from outgoing notification.
        self._unpatch_send_email()
        reply_id = MailThread.message_process('test_xopgi_breaking_cycles.model',
                                              REPLY)
        self.reply = self.env['test_xopgi_breaking_cycles.model'].browse(reply_id)
        thread_index = self.reply.thread_index
        self.verp = self.env['xopgi.verp.record'].search(
            [('thread_index', '=', thread_index)])[0]
        self.return_path = None

        def set_return_path(value):
            self.return_path = value

        def _get_return_path(self, message, *args, **kwargs):
            set_return_path(message.get('Return-Path'))
            return _get_return_path.origin(self, message, *args, **kwargs)

        self.env['ir.mail_server']._patch_method(
            'send_email',
            _get_return_path
        )

    def tearDown(self):
        self._unpatch_send_email()
        super(TestBreakingCycles, self).tearDown()

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

    def send_first_autosubmitted(self):
        first_auto_submitted = FIRST_AUTO_SUBMITTED.format(thread_index=self.verp.reference)
        MailThread = self.env['mail.thread']
        bounce_virtual_id = MailThread.message_process(
            'test_xopgi_verp_router.model',
            first_auto_submitted
        )
        return bounce_virtual_id

    def test_preventing_auto_submitted_cycles(self):
        bounce_virtual_id = self.send_first_autosubmitted()
        first_auto_submitted = self.env['test_xopgi_breaking_cycles.model'].browse(
            bounce_virtual_id.thread_id)
        breaking_address = BreakingCyclesTransport._get_breaking_address(
            self, first_auto_submitted.thread_index)
        self.assertEqual(self.return_path, breaking_address)

    def test_breaking_auto_submitted_cycles(self):
        bounce_virtual_id = self.send_first_autosubmitted()
        first_auto_submitted = self.env['test_xopgi_breaking_cycles.model'].browse(
            bounce_virtual_id.thread_id)
        second_auto_submitted = SECOND_AUTO_SUBMITTED.format(
            thread_index=first_auto_submitted.thread_index)
        MailThread = self.env['mail.thread']
        thread_id = MailThread.message_process(
            'test_xopgi_verp_router.model',
            second_auto_submitted
        )
        thread_found = len(self.env[IGNORE_MESSAGE_ROUTE_MODEL].search([('id', '=', thread_id)]))
        self.assertEqual(thread_found, 1)
