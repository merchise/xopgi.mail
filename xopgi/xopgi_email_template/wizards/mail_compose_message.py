# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.wizards.mail_compose_message
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2015-08-21

from lxml import etree
from lxml.html.diff import htmldiff

from openerp import api, fields, exceptions, models, _

FIND_CLASS_XPATH_EXPRESSION = (
    "descendant-or-self::*[@class and "
    "contains("
    "concat(' ', normalize-space(@class), ' '), "
    "concat(' ', '%s', ' '))]"
)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _have_body_readonly_elements(self):
        return True

    body_readonly_elements = fields.Boolean()
    template_subject_readonly = fields.Boolean(
        related="template_id.use_default_subject")

    @api.multi
    def onchange_template_id(self, template_id, composition_mode, model,
                             res_id):
        ''' Add style to readonly tokens

        '''
        result = super(MailComposeMessage, self).onchange_template_id(
            template_id, composition_mode, model, res_id)
        body = result.get('value', {}).get('body', '')
        if body and template_id:
            doc = etree.HTML(body)
            read_only_elements = doc.xpath(FIND_CLASS_XPATH_EXPRESSION %
                                           'readonly')
            for node in read_only_elements:
                node.set('style', "border: solid; "
                                  "background-color: darkgrey; "
                                  "color: #4C4C4C")
            result['value'].update(
                body_readonly_elements=bool(read_only_elements),
                body=etree.tostring(doc, method='html'))
        return result

    def _validate_template_restrictions(self):
        '''Ensure readonly elements aren't modify.

        '''
        if not self.template_id:
            return True
        template_dict = self.pool['email.template'].generate_email_batch(
            self.env.cr, self.env.uid, self.template_id.id, [self.res_id],
            context=self._context).get(self.res_id, {})
        template_body = template_dict.get('body_html', False)
        if not template_body:
            return True
        template = etree.HTML(template_body)
        result = etree.HTML(self.body)
        result_nodes = result.xpath(FIND_CLASS_XPATH_EXPRESSION % 'readonly')

        def _find_similar(node, candidates):
            '''Find a candidate similar with node, remove it and return
            True, else return False

            '''
            for n in candidates:
                diff = etree.HTML(htmldiff(node, n))
                if not (diff.xpath('descendant-or-self::ins') or
                        diff.xpath('descendant-or-self::del')):
                    candidates.remove(n)
                    return True
            return False
        for node in template.xpath(FIND_CLASS_XPATH_EXPRESSION % 'readonly'):
            if not (result_nodes and _find_similar(node, result_nodes)):
                return False
        self._remove_readonly_style()
        if self.template_id.use_default_subject:
            self.subject = template_dict.get('subject', self.subject)
        return True

    def _remove_readonly_style(self):
        '''Remove style from readonly elements.

        '''
        #  TODO: distinguish readonly style and keep rest
        result = etree.HTML(self.body)
        result_nodes = result.xpath(FIND_CLASS_XPATH_EXPRESSION % 'readonly')
        if result_nodes:
            for node in result_nodes:
                node.attrib.pop('style', False)
                node.attrib.pop('class', False)
            self.body = etree.tostring(result, method='html')

    @api.model
    def send_mail(self):
        ''' Validate no readonly token was modified and remove added style.

        '''
        if self._validate_template_restrictions():
            return super(MailComposeMessage, self).send_mail()
        raise exceptions.ValidationError(
            _('Non-editable items were modified.'))

    @api.multi
    def save_as_template(self):
        ''' Remove added style from readonly tokens.

        '''
        self._remove_readonly_style()
        return super(MailComposeMessage, self).save_as_template()
