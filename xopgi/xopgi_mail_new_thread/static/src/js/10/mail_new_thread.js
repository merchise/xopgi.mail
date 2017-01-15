odoo.define('xopgi_mail.new.thread', function (require) {
'use strict';

var ChatThreadNew = require('mail.ChatThread');

ChatThreadNew.include({
    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self.$el.on(
                'click',
                '.o_thread_message_new_thread',
                _.bind(self.on_message_new_thread, self)
            );
        });
    },

    on_message_new_thread: function(event) {
        // Get the action data and execute it to open the
        // new_thread_wizard
        var do_action = this.do_action,
	    msg_id = $(event.currentTarget).data('message-id');

        this.rpc("/web/action/load", {
            "action_id":
                    "xopgi_mail_new_thread.new_thread_wizard_action"
        }).done(function(action) {
	      action.context = {'default_message_id': msg_id};
              do_action(action);
	});
    }
});

return ChatThreadNew;

});
