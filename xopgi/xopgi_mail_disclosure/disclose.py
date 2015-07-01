#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# disclose
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-06-17

'''Implements a kind of disclosure policy for emails.

Within the footer of an outgoing email, users with a full_email disclosure
will be include, so that others are notified.

.. note:: To protect this implementation from abuse, only 20 users are
   disclosed.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from openerp.models import Model


class Notification(Model):
    _inherit = _name = 'mail.notification'
