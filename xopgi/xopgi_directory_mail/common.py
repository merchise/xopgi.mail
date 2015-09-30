# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_unique_message_id.common
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-02

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)
from openerp import models


class MailThread(models.AbstractModel):
    _name = 'mail.thread'
    _inherit = _name

    def _find_partner_from_emails(self, cr, uid, id, emails, model=None,
                                  context=None, check_followers=True):
        context = dict(context or {}, include_fake=True)
        return super(MailThread, self)._find_partner_from_emails(
            cr, uid, id, emails, model=model, context=context,
            check_followers=check_followers)
