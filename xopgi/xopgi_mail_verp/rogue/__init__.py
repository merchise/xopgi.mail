#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# rogue
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-03-01

'''Rogue bounces.

Rogue bounces are bounces sent to the wrong address.  We *know* they are
bounces via specific probes.  Rogue bounces detectors should only work if they
can find the original thread from which the message was sent.

Most of the time it won't be easy to know the author of message that bounced,
but at least we can place a proper notice for all internal users and remove
the bouncing address.

Probes are basically MailRouter with a different interface.  When any probe
tells us the message is a rogue bounce, we stop checking other probes.

See the interface in `IRogueBounceProber`:class:.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil import logger

from openerp.addons.xopgi_mail_threads import MailRouter
from . import _probes


class RogueBounceProber(MailRouter):
    @classmethod
    def _iter_probes(cls):
        probes = getattr(_probes, '__all__', None)
        if not probes:
            probes = dir(_probes)
        for name in probes:
            probe = getattr(_probes, name, None)
            if isinstance(probe, type) and hasattr(probe, '__call__'):
                yield probe

    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        probe = found = None
        probes = list(cls._iter_probes())
        while not found and probes:
            probe = probes.pop(0)()
            logger.debug('Probing with %s', probe)
            found = probe(message)
            if found and not ('thread_index' in found and 'failures' in found):
                logger.error('Probe returned invalid data',
                             extra=dict(probe=probe, found=found))
                found = None
        if found:
            return True, (probe, found)
        else:
            return False, None

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        probe, values = data
        index = values['thread_index']
        recipients = values['failures']
        MailThread = obj.pool['mail.thread']
        model, thread_id = MailThread._threadref_by_index(cr, uid, index)
        routes[:] = [
            cls._get_route(obj, cr, uid, (None, model, thread_id, recipient, message))
            for recipient in recipients
        ]
        # XXX: Clean up the message so that other routers don't reroute them.
        for header in ('To', 'Cc', 'Delivered-To', 'Resent-To',
                       'Resent-Cc', 'Envelop-To'):
            del message[header]
        return routes

    @classmethod
    def _get_route(self, obj, cr, uid, bouncedata):
        from ..mail_bounce_model import BOUNCE_MODEL
        return (BOUNCE_MODEL, bouncedata, {}, uid, None)
