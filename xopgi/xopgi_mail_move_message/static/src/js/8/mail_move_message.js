
openerp.xopgi_mail_move_message = function (instance) {
    instance.mail.ThreadMessage.include({
        bind_events: function () {
            this._super.apply(this, arguments);
            this.$('.oe_move_message').on('click', this.on_message_move_message);
        },

        init: function (parent, datasets, options) {
            this._super(parent, datasets, options);
            this.can_move = datasets.can_move;
        },

        on_message_move_message: function() {
            // Get the action data and execute it to open the
            // move_message_wizard
            var do_action = this.do_action,
            msg_id = this.id;
            this.rpc("/web/action/load", {
                "action_id":
                    "xopgi_mail_move_message.move_message_wizard_action"
            })
		.done(function(action) {
                    action.context = {
                        'active_id': msg_id,
                        'active_ids': [msg_id]
                    };
                    do_action(action);
		});
        }
    });
};
