from . import mail_move_message_wizard # noqa
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields


FIELD_NAME = 'can_move'


class Message(osv.Model):
    _inherit = 'mail.message'

    def _get_can_move(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        has_group = self.pool['res.users'].has_group(
            cr, uid, 'xopgi_mail_new_thread.group_new_thread')
        for msg in self.browse(cr, uid, ids, context=context):
            result[msg.id] = (msg.type != 'notification' and
                              (uid == SUPERUSER_ID or has_group))
        return result

    _columns = {FIELD_NAME: fields.function(_get_can_move, string='Can New',
                                            type='boolean'), }

    def _message_read_dict(self, cr, uid, msg, parent_id=False, context=None):
        res = super(Message, self)._message_read_dict(
            cr, uid, msg, parent_id=parent_id, context=context)
        res[FIELD_NAME] = getattr(msg, FIELD_NAME)
        return res