odoo.define('xopgi.MailForward', function (require) {
    'use strict';

    var core = require('web.core');
    var ChatThread = require('mail.ChatThread');
    var _t = core._t;

    var chat_manager = require('mail.chat_manager');

    require('mail.chat_client_action');
    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');

    ChatAction.include({
        select_message: function(message_id){
            var message = chat_manager.get_message(message_id);
            var $body = $('<div>'+message.body+'</div>');
            var body = (
                '\n\n' +
                    '----------' +
                    _t('Original message') + '---------- \n' +
                    _t('Re:')+' '+message.record_name + _t('*****')+ '\n' +
                    _t('Subject:') + ' ' + message.subject + '\n' +
                    _t('From:') + ' ' + _.str.escapeHTML(message.author_id[1]) + '\n' +
                    _t('Date:') + ' ' + message.date + '\n\n' +
                    $body.text()
            );
            this.extended_composer.$input[0].value = body;
            this.extended_composer.toggle(true);
            this.extended_composer.focus('body');
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

        on_message_forward: function() {
            var foward_header = _t('Fwd:');
            var subject = [foward_header];
            var subject_parent = [];
            var partner_list = [];
            var partners = this.partner_ids;
            for (var key in partners) {
                partner_list.push(partners[key][1]);
            }

            if (_.string.startsWith(this.subject, foward_header)) {
                subject.pop();
                subject_parent.pop();
            }

            if (this.subject) {
                subject.push(this.subject);
                subject_parent.push(this.subject);
            } else if (this.record_name &&
                       (this.show_record_name || this.parent_id)) {
                subject.push(this.record_name);
                subject_parent.push(this.record_name);
            } else {
                subject.push(this.record_name);
                subject_parent.push(this.record_name);
            }

            var body = (
                '<br/>' +
                    '<p><i>----------' +
                    _t('Original message') +
                    '----------<br/>' +
                    _t('Subject:') + ' ' +subject_parent + '<br/>' +
                    _t('From:') + ' ' +
                    //_.str.escapeHTML(this.author_id[1]) + '<br/>' +
                    _.str.escapeHTML('') + '<br/>' +
                    _t('To:') + ' ' +
                    _.str.escapeHTML(partner_list) + '<br/>' +
                    _t('Date:') + ' ' + this.date + '</i></p><br/>' +

                    this.body
            );

            var context = {
                default_attachment_ids: this.attachment_ids,
                default_body: body,
                default_model: this.model,
                default_res_id: this.res_id,
                default_subject: subject.join(" "),
                mail_post_autofollow: true
            };
            var do_action = this.do_action;
            var self = this;

            this.rpc(
                "/web/action/load",
                {"action_id": "xopgi_mail_forward.compose_action"}
            ).done(function(action) {
                action.context = context;
                do_action(action, {'on_close': function(){
                    // self.parent_thread.message_fetch();
                }});
            });
        }
    });

});

// Local Variables:
// indent-tabs-mode: nil
// End:
