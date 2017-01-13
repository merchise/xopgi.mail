dict(
    # Internal addon, it should be auto-installed when both no-wall and
    # forward are installed.
    depends=['xopgi_mail_nowall', 'xopgi_mail_forward'],
    name='xopgi_mail_nowall_forward',
    summary='Makes the no-replying from wall be activated for forwarding',
    description='Makes the no-replying from wall be activated for forwarding',
    application=False,

    data=[
        'views/assets.xml',
    ],

    auto_install=True,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

)
