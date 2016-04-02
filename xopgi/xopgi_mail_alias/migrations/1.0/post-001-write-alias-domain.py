# -*- encoding: utf-8 -*-
# ----------------------------------------------------------------------
# post-001-write-alias-domain
# ----------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-01

'''Update Alias Domain values.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoutil.modules import modulemethod
from openerp import SUPERUSER_ID


@modulemethod
def migrate(self, cr, version):
    from openerp.modules.registry import RegistryManager as manager
    self.pool = manager.get(cr.dbname)
    self.create_crons(cr)


@modulemethod
def create_crons(self, cr):
    from openerp.addons.xopgi_mail_alias.mail_alias \
        import MailAlias, get_default_alias_domain
    from xoeuf.osv.orm import get_modelname
    alias_obj = self.pool[get_modelname(MailAlias)]
    alias_ids = alias_obj.search(cr, SUPERUSER_ID, [])
    domain = get_default_alias_domain(self.pool, cr, SUPERUSER_ID)
    if not alias_ids:
        return
    alias_obj.write(cr, SUPERUSER_ID, alias_ids, {'alias_domain': domain})
