dict(
    name='Avoid replying from the wall',
    depends=['mail', ],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=ODOO_VERSION_INFO[0] in (8, 9, 10),   # noqa

    application=False,
    category='Mail',
    summary=('Disallows replying from the wall, effectively disallowing '
             'replying to direct emails before converting them to '
             'proper object'),
    data=[
        'views/%d/assets.xml' % ODOO_VERSION_INFO[0],   # noqa
    ]
)
