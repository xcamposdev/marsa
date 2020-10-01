# -*- coding: utf-8 -*-

import logging
import base64
import re

from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class mail_custom_0(models.TransientModel):

    _inherit = 'mail.compose.message'


    def get_mail_values(self, res_ids):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        # render all template-based value at once
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            records = self.env[self.model].browse(res_ids)
            reply_to_value = self.env['mail.thread']._notify_get_reply_to_on_records(default=self.email_from, records=records)

        blacklisted_rec_ids = []
        if mass_mail_mode and issubclass(type(self.env[self.model]), self.pool['mail.thread.blacklist']):
            BL_sudo = self.env['mail.blacklist'].sudo()
            blacklist = set(BL_sudo.search([]).mapped('email'))
            if blacklist:
                targets = self.env[self.model].browse(res_ids).read(['email_normalized'])
                # First extract email from recipient before comparing with blacklist
                blacklisted_rec_ids.extend([target['id'] for target in targets
                                            if target['email_normalized'] and target['email_normalized'] in blacklist])

        for res_id in res_ids:
            # static wizard (mail.message) values
            
            ##########################
            reply_follower = ""
            # ADD REPLY FOLLOWERS
            if(self.model == 'sale.order'):
                sale_order = self.env['sale.order'].search([('id','=', self.res_id)])
                
                emails_follower = []
                if(sale_order.message_follower_ids):
                    for partner in sale_order.message_follower_ids.partner_id:
                        if(partner.email):
                            emails_follower.append(partner.email)

                if(emails_follower):
                    reply_follower = ','.join(emails_follower)
                    
            ##########################

            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
                'reply_to': reply_follower ###########################
            }

            # mass mailing: rendering override wizard static values
            if mass_mail_mode and self.model:
                record = self.env[self.model].browse(res_id)
                mail_values['headers'] = record._notify_email_headers()
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(notification=not self.auto_delete_message, model=self.model, res_id=res_id, record_name=False)
                # auto deletion of mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy({'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values['attachment_ids'] = self.env['mail.thread']._message_post_process_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids,
                    {'model': 'mail.message', 'res_id': 0}
                )['attachment_ids']
                # Filter out the blacklisted records by setting the mail state to cancel -> Used for Mass Mailing stats
                if res_id in blacklisted_rec_ids:
                    mail_values['state'] = 'cancel'
                    # Do not post the mail into the recipient's chatter
                    mail_values['notification'] = False

            results[res_id] = mail_values
        return results

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        values = self.onchange_template_id(self.template_id.id, self.composition_mode, self.model, self.res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        if template_id and composition_mode == 'mass_mail':
            template = self.env['mail.template'].browse(template_id)
            fields = ['subject', 'body_html', 'email_from', 'reply_to', 'mail_server_id']
            values = dict((field, getattr(template, field)) for field in fields if getattr(template, field))
            if template.attachment_ids:
                values['attachment_ids'] = [att.id for att in template.attachment_ids]
            if template.mail_server_id:
                values['mail_server_id'] = template.mail_server_id.id
            if template.user_signature and 'body_html' in values:
                signature = self.env.user.signature
                values['body_html'] = tools.append_content_to_html(values['body_html'], signature, plaintext=False)
        elif template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if email not send

            attachment_ids = []
            ##########################
            if(model == 'sale.order'):
                sale_order = self.env['sale.order'].search([('id','=', self.res_id)])
                
                if(sale_order and sale_order.x_studio_oportunidad):
                    crm_lead = self.env['crm.lead'].search([('id','=',sale_order.x_studio_oportunidad.id)])
                    if(crm_lead):
                        
                        crm_attachment_ids = self.env['ir.attachment'].search(['&',('res_model','=','crm.lead'),('res_id', '=', crm_lead.id)])
                        if(crm_attachment_ids):
                            for line in crm_attachment_ids:
                                attachment_ids.append(line.id)
                        
                        # sale_order_attachment_ids = self.env['ir.attachment'].search(['&',('res_model','=','sale.order'),('res_id', 'in', crm_lead.order_ids.ids)])
                        # if(sale_order_attachment_ids):
                        #     attachment_ids.append(sale_order_attachment_ids.ids)

                        for line in crm_lead.order_ids:
                            if(line.state == 'draft' and line.id != res_id):
                                template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(line.id, fields=['attachment_ids'])
                                values['attachments'].append(template_values['attachments'][0])


            ##########################

            Attachment = self.env['ir.attachment']
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'res_model': 'mail.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            if values.get('attachment_ids', []) or attachment_ids:
                values['attachment_ids'] = [(6, 0, values.get('attachment_ids', []) + attachment_ids)]
        else:
            default_values = self.with_context(default_composition_mode=composition_mode, default_model=model, default_res_id=res_id).default_get(['composition_mode', 'model', 'res_id', 'parent_id', 'partner_ids', 'subject', 'body', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'])
            values = dict((key, default_values[key]) for key in ['subject', 'body', 'partner_ids', 'email_from', 'reply_to', 'attachment_ids', 'mail_server_id'] if key in default_values)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')

        # This onchange should return command instead of ids for x2many field.
        values = self._convert_to_write(values)

        return {'value': values}

    @api.model
    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        """ Call email_template.generate_email(), get fields relevant for
            mail.compose.message, transform email_cc and email_to into partner_ids """
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc',  'reply_to', 'attachment_ids', 'mail_server_id']
        returned_fields = fields + ['partner_ids', 'attachments']
        values = dict.fromkeys(res_ids, False)

        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if template_values[res_id].get(field))
            res_id_values['body'] = res_id_values.pop('body_html', '')
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]
