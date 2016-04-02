#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_nowall
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-24

'''Disallow receiving direct mail.

.. warning:: We recommend to explicitly bounce direct mail, this module DOES
   NOT do that.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.addons.xopgi_mail_threads.routers import MailRouter


MODEL_INDEX = 0
DIRECT_MAIL_MODEL = 'res.users'


class NoDirectMailRouter(MailRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        return True

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        routes[:] = [route
                     for route in routes
                     if route[MODEL_INDEX] != DIRECT_MAIL_MODEL]
        return routes
