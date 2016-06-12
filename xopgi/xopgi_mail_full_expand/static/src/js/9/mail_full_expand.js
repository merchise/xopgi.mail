odoo.define('xopgi.mail.Expand', function (require) {
'use strict';

var ChatThread = require('mail.ChatThread');

ChatThread.include({
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self.$el.on(
                'click',
                '.o_thread_message_expand',
                _.bind(self.on_message_full_expand, self)
            );
        });
    },

    on_message_full_expand: function(event) {
        // Get the action data and execute it to open the full view
        var do_action = this.do_action,
            msg_id = $(event.currentTarget).data('message-id');

        this.rpc("/web/action/load", {
            "action_id": "xopgi_mail_full_expand.act_window",
        }).done(function(action) {
            action.res_id = msg_id;
            do_action(action);
        });
    }
});

return ChatThread;

});
