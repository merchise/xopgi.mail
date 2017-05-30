from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

try:
    from odoo.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from openerp.release import version_info as ODOO_VERSION_INFO


if (8, 0) <= ODOO_VERSION_INFO < (11, 0):
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import thread_address  # noqa
