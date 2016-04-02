# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# evaneos_mailrouter
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-22

'''A MailRouter for messages delivered via Evaneos MTA.


'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from openerp.addons.xopgi_mail_threads import MailRouter


class EvaneosMailRouter(MailRouter):
    @staticmethod
    def get_senders(msg):
        from email.utils import getaddresses
        headers = ['Sender', 'From']
        senders = []
        get = msg.get_all
        for header in headers:
            senders.extend(email for _, email in getaddresses(get(header, [])))
        return senders

    @classmethod
    def get_all_matches(cls, obj, cr, uid, message):
        from six.moves import map
        from re import compile as _re_compile
        config = obj.pool['ir.config_parameter']
        pattern = config.get_param(
            cr, uid, 'evaneos.mailrouter.pattern',
            # The default allows to tests pass.
            default=r'_(?P<thread>\d+)@.*(?<=[@\.])evaneos\.com$'
        )
        senders = cls.get_senders(message)
        regex = _re_compile(pattern)
        search = regex.search
        return (match for match in map(search, senders) if match)

    @classmethod
    def get_first_match(cls, obj, cr, uid, message):
        return next(cls.get_all_matches(obj, cr, uid, message), None)

    @classmethod
    def query(cls, obj, cr, uid, message, context=None):
        match = cls.get_first_match(obj, cr, uid, message)
        return bool(match), match

    @classmethod
    def apply(cls, obj, cr, uid, routes, message, data=None, context=None):
        from xoeuf.osv.model_extensions import search_browse
        match = data
        sender = match.group(0)
        fmodel, fthread = 0, 1
        escape = lambda s: s.replace('_', r'\_').replace('%', r'\%')
        # The query for any email from the same sender that has a resource id,
        # but its parent has no parent:  Explanation:  When a new message from
        # Evaneos arrives OpenERP actually creates two messages: A
        # Notification for the recently created Lead and the original
        # message.  Strangely enough, the notification is the "parent" of the
        # message that actually started everything.
        #
        # The query is in prefix notation, but some ANDs are omitted since
        # they are implied.
        query = [
            '&',

            '|',
            ('email_from', '=like', "%%%s" % escape(sender)),   # Ends with _XXX@..
            ('email_from', '=like', '%%%s>' % escape(sender)),  # or _XXX@..>

            ('parent_id.parent_id', '=', None),
            ('res_id', '!=', 0),
            ('res_id', '!=', None)]
        mail_message = obj.pool['mail.message']
        result = search_browse(mail_message, cr, uid, query, ensure_list=True)
        if result:
            # search_browse may return a list or a single browse record
            result = result[0] if isinstance(result, list) else result
            model = result.model
            thread_id = result.res_id
            # Find the matching route. The matching route is the first its
            # model is the same as the one found in the root message and
            # its thread id is not set (i.e would create a new
            # conversation).
            pred = lambda r: (r[fmodel] == model and
                              (not r[fthread] or r[fthread] == thread_id))
            i, route = next(cls.find_route(routes, pred), (None, None))
            if route:
                routes[i] = (model, thread_id, ) + route[2:]
            else:
                # Odoo routes are 5-tuple.  The last is the alias
                # record.  Best not to pass any.
                routes.append((model, thread_id, {}, uid, None))
