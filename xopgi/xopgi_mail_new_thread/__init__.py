try:
    from openerp.release import version_info as ODOO_VERSION_INFO
except ImportError:
    from odoo.release import version_info as ODOO_VERSION_INFO

if ODOO_VERSION_INFO < (9, 0):
    from . import wizard  # noqa
    from . import new_thread  # noqa
