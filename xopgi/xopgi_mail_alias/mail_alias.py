# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_mail_verp.router
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-10

'''A MailRouter for bounced messages.


For each outgoing message we create unique bounce address (VERP_) of the
form::

   <alias>+<unique bounce reference>

The `unique bounce reference` is a pseudo-random chain of chars and digits
that is kept in a index and maps to:

- The message being sent
- The thread the message belongs to.
- The recipient to which this bounce reference was generated.

  .. note:: A single message may be sent to several recipients.  However, we
     generate an email per recipient.

.. warning:: Bounces should never fail.

   When processing a bounce message, we SHOULD NEVER fail.  This could be done
   at the MTA level, since a bounce should not contain a MAIL FROM.

As noted in SRS_ does not scale.  But neither does Odoo.


.. _VERP: https://en.wikipedia.org/wiki/Variable_envelope_return_path
.. _SRS: https://en.wikipedia.org/wiki/Sender_Rewriting_Scheme

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.models import Model
from openerp.osv import fields
from openerp.addons.xopgi_mail_threads import MailRouter, MailTransportRouter
from openerp.addons.mail.mail_thread import decode_header
from openerp import tools


def get_default_alias_domain(pool, cr, uid, context=None):
    '''

    '''
    get_param = pool['ir.config_parameter'].get_param
    res = get_param(cr, uid, 'mail.catchall.domain', '', context=context)
    return res


class MailAlias(Model):
    _inherit = 'mail.alias'

    _columns = dict(
        alias_domain=fields.char('Alias domain')
    )

    _defaults = dict(
        alias_domain=lambda s, c, u, ctx: get_default_alias_domain(
            s.pool, c, u, context=ctx)
    )

    def fields_get(self, *args, **kargs):
        # Hack to make alias_domain editable. I don't know why it's not!
        result = super(MailAlias, self).fields_get(*args, **kargs)
        alias_domain = result.get('alias_domain', None)
        if alias_domain:
            alias_domain['readonly'] = 0
        return result


class AliasMailRouter(MailRouter):
    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        return True, None

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        result = []
        rcpt_tos = tools.email_split(
            ','.join([decode_header(message, 'Delivered-To'),
                      decode_header(message, 'To'),
                      decode_header(message, 'Cc'),
                      decode_header(message, 'Resent-To'),
                      decode_header(message, 'Resent-Cc')])
        )
        for route in routes:
            alias = route[-1] if len(route) == 5 else None
            if alias:
                alias_mail = '%s@%s' % (alias.alias_name, alias.alias_domain)
                if rcpt_tos and any(alias_mail == rcpt for rcpt in rcpt_tos):
                    result.append(route)
            else:
                result.append(route)
        routes[:] = result
        return routes