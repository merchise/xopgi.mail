# -*- coding: utf-8 -*-
dict(
    name='xopgi.posting_group',
    summary='Allow to enable/disable auto-subscription in groups',

    author='Merchise Autrement',
    category='Hidden',
    version='1.0',
    depends=['mail', ],
    data=['views/mail_group_view.xml', ],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa
)
