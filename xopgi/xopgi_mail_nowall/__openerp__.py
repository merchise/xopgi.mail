dict(
    name='Avoid replying from the wall',
    depends=['mail', ],

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    application=False,
    category='Mail',
    summary=('Disallows replying from the wall, effectively disallowing '
             'replying to direct emails before converting them to '
             'proper object'),
    data=[
        'views/assets.xml',
    ]
)
