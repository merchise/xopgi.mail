
openerp.xopgi_mail_forward = function (instance) {
    var _t = instance.web._t;
    instance.mail.ThreadMessage.include({
        bind_events: function () {
            this._super.apply(this, arguments);
            this.$('.oe_forward').on('click', this.on_message_forward);
        },

        on_message_forward: function () {
            // Generate email subject as possible from record_name and subject
            foward_header = _t('Fwd:');
            subject = [foward_header];
            if (_.string.startsWith(this.subject, foward_header)) {
                subject.pop();
            }

            if (this.subject) {
                subject.push(this.subject);
            } else if (this.record_name &&
                       (this.show_record_name || this.parent_id)) {
                subject.push(this.record_name);
            } else {
                subject = []
            }

            body = (
                '<br/>' +
                '<p><i>----------' +
                _t('Original message') +
                '----------<br/>' +
                _t('From:') + ' ' +
                _.str.escapeHTML(this.author_id[1]) + '<br/>' +
                _t('Date:') + ' ' + this.date + '</i></p><br/>' +
                this.body
            )

            var context = {
                default_attachment_ids: this.attachment_ids,
                default_body: body,
                default_model: this.model,
                default_res_id: this.res_id,
                default_subject: subject.join(" "),
            };

            // Get the action data and execute it to open the composer wizard
            var do_action = this.do_action;
            this.rpc(
                "/web/action/load",
                {
                    "action_id": "xopgi_mail_forward.compose_action",
                }
            ).done(function(action) {
                action.context = context;
                do_action(action);
            });
        }
    });
};
