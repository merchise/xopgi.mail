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


from openerp import tools, SUPERUSER_ID
from openerp.models import Model


def first(iterable, howmany=25):
    from six.moves import zip, range
    return (item for item, _ in zip(iterable, range(howmany)))


# XXX: For now, we simply replace the entire function in the signature...
class Notification(Model):
    _inherit = _name = 'mail.notification'

    def get_signature_footer(self, cr, uid, user_id, res_model=None,
                             res_id=None, context=None, user_signature=True):
        footer = ""
        if not user_id:
            return footer

        # add user signature
        user = self.pool.get("res.users").browse(cr, SUPERUSER_ID, [user_id],
                                                 context=context)[0]
        if user_signature:
            if user.signature:
                signature = user.signature
            else:
                signature = "--<br />%s" % user.name
            footer = tools.append_content_to_html(footer,
                                                  signature, plaintext=False)
        if res_model and res_id:
            message = self.pool[res_model].browse(cr, SUPERUSER_ID, res_id)
            recipients = ', '.join(
                first(partner.name
                      for partner in message.message_follower_ids
                      if partner and partner.name)
            ) + '...'
            if recipients:
                footer += '<br/>'
                disclosed = 'Cc: ' + recipients + '<br/>'
                footer = tools.append_content_to_html(footer,
                                                      disclosed,
                                                      plaintext=False,
                                                      container_tag='div')
        return footer
