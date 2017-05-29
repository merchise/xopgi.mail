#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# coordinated
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~], and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-06-29

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


try:
    from odoo.addons.xopgi_mail_threads import MailRouter
except ImportError:
    from openerp.addons.xopgi_mail_threads import MailRouter

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
