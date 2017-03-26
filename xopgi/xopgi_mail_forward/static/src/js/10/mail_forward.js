odoo.define('xopgi.MailForward', function (require) {
    'use strict';

    var core = require('web.core');
    var ChatThread = require('mail.ChatThread');
    var utils = require('mail.utils');

    var chat_manager = require('mail.chat_manager');
    var composer = require('mail.composer');
    var chatter = require('mail.Chatter');
    var session = require('web.session');
    var Model = require('web.Model');

    var ComposeModel = new Model('mail.compose.message', session.user_context);

    require('mail.chat_client_action');
    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');

    ChatAction.include({
        select_message: function(message_id){
            this._super(message_id);
            var self = this;
            ComposeModel.call(
                'get_forward_action',
                [message_id]
            ).then(function(result) {
                var body = result.context.default_body;
                var $body = $('<div>'+body+'</div>');
                self.extended_composer.$input[0].value = $body.text();
            });
        }
    });

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
                self.do_action(result,
                {
                    on_close: function() {
                        self.trigger('need_refresh');
                        var parent = self.getParent();
                        chat_manager.get_messages({
                            model: parent.model, res_id: parent.res_id
                        });
                  }
                }).then(self.trigger.bind(self, 'close_composer'));
            });
        }
    });

});

// Local Variables:
// indent-tabs-mode: nil
// End:
