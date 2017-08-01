from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import MAJOR_ODOO_VERSION


if 8 <= MAJOR_ODOO_VERSION < 11:
    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.

    from . import servers  # noqa
