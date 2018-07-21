{
    'name': 'test_xopgi_evaneos_mailrouter',
    'author': 'Merchise Autrement',
    'depends': ['xopgi_evaneos_mailrouter', 'xopgi_mail_threads', 'crm'],
    'post_init_hook': '_assert_test_mode',
}
