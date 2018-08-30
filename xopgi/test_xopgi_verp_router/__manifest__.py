{
    'name': 'test_xopgi_verp_router',
    'author': 'Merchise Autrement',
    'depends': ['xopgi_mail_verp'],
    'post_init_hook': '_assert_test_mode',
    'data': ['data/init.xml'],
}
