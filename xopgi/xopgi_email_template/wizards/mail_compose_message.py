# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_email_template.template
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

from openerp import api, exceptions, models


FIND_CLASS_XPATH_EXPRESSION = (
    "descendant-or-self::*[@class and "
    "contains("
    "concat(' ', normalize-space(@class), ' '), "
    "concat(' ', '%s', ' '))]"
)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

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
            for node in doc.xpath(FIND_CLASS_XPATH_EXPRESSION % 'readonly'):
                node.set('style', "border: solid; "
                                  "background-color: darkgrey; "
                                  "color: #4C4C4C")
            result['value']['body'] = etree.tostring(doc, method='html')
        return result

    def _validate_template_restrictions(self):
        '''Ensure readonly elements aren't modify.

        '''
        if not self.template_id:
            return True
        template_body = self.pool['email.template'].generate_email_batch(
            self.env.cr, self.env.uid, self.template_id.id, [self.res_id],
            fields=['body_html'], context=self._context)
        template_body = template_body.get(self.res_id, {}).get('body_html')
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
            self.body = etree.tostring(result, method='html')

    @api.model
    def send_mail(self):
        ''' Validate no readonly token was modified and remove added style.

        '''
        if self._validate_template_restrictions():
            return super(MailComposeMessage, self).send_mail()
        raise exceptions.ValidationError('modificaste áreas no editables')

    @api.multi
    def save_as_template(self):
        ''' Remove added style from readonly tokens.

        '''
        self._remove_readonly_style()
        return super(MailComposeMessage, self).save_as_template()
