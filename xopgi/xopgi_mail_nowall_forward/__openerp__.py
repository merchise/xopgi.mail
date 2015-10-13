dict(
    # Internal addon, it should be auto-installed when both no-wall and
    # forward are installed.
    auto_install=True,
    depends=['xopgi_mail_nowall', 'xopgi_mail_foward'],
    name='xopgi_mail_nowall_forward',
    summary='Makes the no-replying from wall be activated for forwarding',
    description='Makes the no-replying from wall be activated for forwarding',
    application=False,
    installable=True,
    data=[
        'view/assets.xml',
    ],
)
