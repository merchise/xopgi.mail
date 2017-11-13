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

from xoeuf.odoo.addons.xopgi_mail_threads import MailRouter

from .standard import BouncedMailRouter as StandardBounceRouter
from .rogue import RogueBounceProber


class CoordinatedBounceRouter(MailRouter):
    '''Coordinates the BouncedMailRouter with the rogue bounce detector.

    The rogue bounce detector is only queried as a fallback for the standard
    bounce detector.

    '''
    @classmethod
    def query(cls, obj, message):
        candidates = [StandardBounceRouter, RogueBounceProber]
        router = res = data = None
        while candidates and not res:
            router = candidates.pop(0)
            res = router.query(obj, message)
            if isinstance(res, tuple):
                res, data = res
            else:
                data = None
        if res:
            return res, (router, data)
        else:
            return False, None

    @classmethod
    def apply(cls, obj, routes, message, data=None):
        router, data = data
        return router.apply(obj, routes, message, data=data)
