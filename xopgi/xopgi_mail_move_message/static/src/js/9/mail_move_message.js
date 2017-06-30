odoo.define('xopgi_mail.message.move', function (require) {
'use strict';

var ChatThreadMove = require('mail.ChatThread');

ChatThreadMove.include({
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self.$el.on(
                'click',
                '.o_thread_message_move',
                _.bind(self.on_message_move_message, self)
            );
        });
    },

    on_message_move_message: function(event) {
        // Get the action data and execute it to open the
        // move_message_wizard
        var do_action = this.do_action,
	    msg_id = $(event.currentTarget).data('message-id');

        this.rpc("/web/action/load", {
            "action_id":
                    "xopgi_mail_move_message.move_message_wizard_action"
        }).done(function(action) {
	            action.context = {
                        'active_id': msg_id,
                        'active_ids': [msg_id]
                    };
                    do_action(action);
	});
    }
});

return ChatThreadMove;

});
