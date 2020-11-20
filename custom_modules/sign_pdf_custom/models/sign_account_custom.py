# -*- coding: utf-8 -*-

import logging
import base64
import requests
import json
from odoo import api, fields, models, exceptions, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class sign_account_custom_0(models.TransientModel):

    _inherit = 'mail.compose.message'


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
            Attachment = self.env['ir.attachment']
            for attach_fname, attach_datas in values.pop('attachments', []):

                ###########################################################

                if(self.model == "account.move" and self.res_id > 0 and self.template_id != False and self.template_id.model == "account.move"):
                    sign_pdf_api = self.env['ir.config_parameter'].get_param('x_sign_pdf_url_api')
                    api_token = self.env['ir.config_parameter'].get_param('x_api_token')
                    paramaters = {
                        'api_token': str(api_token),
                        'pdf_file': attach_datas.decode('utf-8') 
                    }
                    #.decode('utf-8')

                    pdf_sign = requests.post(\
                        sign_pdf_api, 
                        headers={'Content-type': 'application/json', 'Accept': 'application/json'}, \
                        data=json.dumps(paramaters))

                    if(pdf_sign):
                        if(pdf_sign.status_code == 200):
                            response_sign = json.loads(pdf_sign.text)
                            attach_datas = response_sign['certified_file']
                    
                ###########################################################

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

    # def download_document(self, product_ids, type, **kw):
    #     product_ids = json.loads(product_ids)
    #     attachment_ids = request.env['ir.attachment'].search(['&',('res_model','=','product.template'),('res_id', 'in', product_ids)])
    #     file_dict = {}
    #     for attachment_id in attachment_ids:
    #         file_name = attachment_id.name.replace(".pdf","")
    #         if (type == "ficha_ESP"):
    #             if(len(file_name) > 2 and file_name.startswith('2')):
    #                 file_store = attachment_id.store_fname
    #                 if file_store:
    #                     file_name = attachment_id.name
    #                     file_path = attachment_id._full_path(file_store)
    #                     file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)    
    #         elif (type == "ficha_EN"):
    #             if(len(file_name) == 2):
    #                 file_store = attachment_id.store_fname
    #                 if file_store:
    #                     file_name = attachment_id.name
    #                     file_path = attachment_id._full_path(file_store)
    #                     file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)    
    #         elif (type == "Cert"):
    #             if(len(file_name) > 2 and file_name.startswith('1')):
    #                 file_store = attachment_id.store_fname
    #                 if file_store:
    #                     file_name = attachment_id.name
    #                     file_path = attachment_id._full_path(file_store)
    #                     file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
    #     zip_filename = datetime.now()
    #     zip_filename = "%s.zip" % zip_filename
    #     bitIO = BytesIO()
    #     zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
    #     for file_info in file_dict.values():
    #         zip_file.write(file_info["path"], file_info["name"])
    #     zip_file.close()
    #     return request.make_response(bitIO.getvalue(),
    #                                  headers=[('Content-Type', 'application/x-zip-compressed'),
    #                                           ('Content-Disposition', content_disposition(zip_filename))])

