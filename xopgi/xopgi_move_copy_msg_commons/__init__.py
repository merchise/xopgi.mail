from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp.release import version_info as ODOO_VERSION_INFO


# Although we're installable in Odoo 9 we do se to easy migration from Odoo 8
# to Odoo 10.
if ODOO_VERSION_INFO[0] in (8, 10):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import common  # noqa
    from . import mail_config  # noqa
