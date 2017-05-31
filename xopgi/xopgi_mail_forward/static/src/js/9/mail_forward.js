odoo.define('xopgi.mail.MailForward', function (require) {
    'use strict';

    var ChatThread = require('mail.ChatThread');
    var session = require('web.session');
    var Model = require('web.Model');
    var ComposeModel = new Model('mail.compose.message', session.user_context);

    ChatThread.include({
        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function(){
                self.$el.on(
                    'click',
                    '.o_thread_message_forward',
                    _.bind(self.on_message_forward, self)
                );
            });

        },

        on_message_forward: function(event) {
            var message_id = $(event.currentTarget).data('message-id');
            var self = this;
            ComposeModel.call('get_forward_action', [message_id]).then(function(result) {
                self.do_action(
                    result,
                    {
                        on_close: function() {
                            self.trigger('need_refresh');
                            var parent = self.getParent();
                        }
                    }
                ).then(self.trigger.bind(self, 'close_composer'));
            });
        }
    });

});

// Local Variables:
// indent-tabs-mode: nil
// End:
