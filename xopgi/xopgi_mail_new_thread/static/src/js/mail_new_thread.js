
openerp.xopgi_mail_new_thread = function (instance) {
    instance.mail.ThreadMessage.include({
        bind_events: function () {
            this._super.apply(this, arguments);
            this.$('.oe_new_thread').on('click', this.on_message_new_thread);
        },

        init : function (parent, datasets, options){
            this._super(parent, datasets, options);
            this.can_new_thread = datasets.can_new_thread;
        },

        on_message_new_thread: function() {
            // Get the action data and execute it to open the
            // new_thread_wizard
            var do_action = this.do_action,
            msg_id = this.id;
            this.rpc("/web/action/load", {
                "action_id": "xopgi_mail_new_thread.new_thread_wizard_action",
            })
		.done(function(action) {
                    action.context = {'default_message_id': msg_id};
                    do_action(action);
		});
        }
    });
};
