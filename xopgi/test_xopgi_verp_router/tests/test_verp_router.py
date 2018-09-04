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
from odoo.modules import module
from xoeuf.odoo.addons.xopgi_mail_threads.stdroutes import \
    IGNORE_MESSAGE_ROUTE_MODEL

FIRST = '''\
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

BOUNCE = '''\
From: =User <user@example.com>
Subject: RE: Reply
Message-Id: 1
To: <bounces+{thread_index}@example.com>

This is the message data.
'''


class TestVerpRouter(TransactionCase):
    at_install = False
    post_install = not at_install

    def setUp(self):
        super(TestVerpRouter, self).setUp()
        MailThread = self.env['mail.thread']
        Partner = self.env['res.partner']
        obj_id = MailThread.message_process('test_xopgi_verp_router.model',
                                            FIRST)
        obj = self.env['test_xopgi_verp_router.model'].browse(obj_id)
        obj.message_subscribe(Partner.create(dict(
            name='Other Address',
            email='other_test@lahavane.com',
        )).ids)
        self._unpatch_send_email()
        reply_id = MailThread.message_process('test_xopgi_verp_router.model',
                                              REPLY)
        self.reply = self.env['test_xopgi_verp_router.model'].browse(reply_id)
        thread_index = self.reply.thread_index
        self.verp = self.env['xopgi.verp.record'].search(
            [('thread_index', '=', thread_index)])[0]

    def tearDown(self):
        super(TestVerpRouter, self).tearDown()

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

    def test_standard_verp_router(self):
        bounce = BOUNCE.format(thread_index=self.verp.reference)
        MailThread = self.env['mail.thread']
        virtual_id = MailThread.message_process(
            'test_router.model',
            bounce
        )
        self.assertEqual(self.reply[0].id,
                         virtual_id.thread_id)

    def test_ignore_standard_verp_mail_when_no_thread_found(self):
        bounce = BOUNCE.format(thread_index=self.verp.reference)
        MailThread = self.env['mail.thread']
        MailThread.sudo()._thread_by_index(self.reply[0].thread_index).unlink()
        thread_id = MailThread.message_process(
            'test_xopgi_verp_router.model',
            bounce
        )
        thread_found = self.env[IGNORE_MESSAGE_ROUTE_MODEL].browse(thread_id)
        self.assert_(thread_found)

    def test_rogue_verp_router(self):
        MailThread = self.env['mail.thread']
        message_fname = module.get_module_resource(
            'test_xopgi_verp_router',
            'data',
            'rogue-nauta.eml'
        )
        with open(message_fname, 'rb') as f:
            nauta_message = f.read()
        # Get thread_index for replacement
        parts = nauta_message.split('X-Odoo-Thread-Index:', 1)
        thread_index = parts[1].split('Thread-Index')[0].strip()
        nauta_msg = nauta_message.replace(thread_index,
                                          self.reply[0].thread_index)
        virtual_id = MailThread.message_process(
            'test_xopgi_verp_router.model',
            nauta_msg
        )
        self.assertEqual(self.reply[0].id,
                         virtual_id.thread_id)

    def test_ignore_rogue_verp_when_no_thread_found(self):
        MailThread = self.env['mail.thread']
        message_fname = module.get_module_resource(
            'test_xopgi_verp_router',
            'data',
            'rogue-nauta.eml'
        )
        with open(message_fname, 'rb') as f:
            nauta_message = f.read()
        thread_id = MailThread.message_process(
            'test_xopgi_verp_router.model',
            nauta_message
        )
        thread_found = self.env[IGNORE_MESSAGE_ROUTE_MODEL].browse(thread_id)
        self.assertTrue(thread_found)
