try:
    from openerp.release import version_info as VERSION_INFO
except ImportError:  # Odoo 10+
    from odoo.release import version_info as VERSION_INFO

from . import test_verp


if VERSION_INFO < (8, 0):
    checks = [
        test_verp,
    ]
