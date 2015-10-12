dict(
    name='Avoid replying from the wall',
    depends=['mail', ],
    installable=True,
    application=False,
    category='Mail',
    summary=('Disallows replying from the wall, effectively disallowing '
             'replying to direct emails before converting them to '
             'proper object'),
    data = [
        'views/assets.xml',
    ]
)
