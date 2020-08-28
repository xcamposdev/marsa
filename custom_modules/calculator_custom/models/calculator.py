# -*- coding: utf-8 -*-

import logging
import copy
from decimal import Decimal
from odoo import api, fields, models, exceptions, _
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class calculator_custom_0(models.Model):

    _inherit = 'sale.order'

    ENCIMERA = "Material"
    ENCIMERA2 = "Material"
    APLACADO = "Material"
    SERVICIO = "Servicio"
    ZOCALO = "Material"
    CANTO = "Canto"
    OPERACION = "Operaciones"
    PRODUCT_DESCOUNT_NAME = "Descuento"
    PRODUCT_MERMA_NAME = "Material Sobrante"

    SECTION_ENCIMERA = "Sección Encimera"
    SECTION_APLACADO = "Sección Aplacado"
    SECTION_SERVICIO = "Sección Servicio"
    SECTION_ZOCALO = "Sección Zocalo"
    SECTION_CANTO = "Sección Canto"
    SECTION_OPERACION = "Sección Operacion"
    SECTION_DESCUENTOS = "Sección Descuentos"

    PRODUCT_MERMA_ID = fields.Integer(store=False, default=lambda self: self.env['product.product'].search([('name','=',self.PRODUCT_MERMA_NAME)], limit=1))
    custom_encimera = fields.Many2one('product.template', "Encimera", domain=[('categ_id.name','=',ENCIMERA)], store='FALSE')
    custom_encimera2 = fields.Many2one('product.template', "Encimera 2", domain=[('categ_id.name','=',ENCIMERA2)], store='FALSE')
    custom_aplacado = fields.Many2one('product.template', "Aplacado", domain=[('categ_id.name','=',APLACADO)], store='FALSE')
    custom_servicio = fields.Many2one('product.template', "Servicio", domain=[('categ_id.name','=',SERVICIO)], store='FALSE')
    custom_zocalo = fields.Many2one('product.template', "Zocalo", domain=[('categ_id.name','=',ZOCALO)])
    custom_canto = fields.Many2one('product.template', "Canto", domain=[('categ_id.name','=',CANTO)])
    custom_operacion = fields.Many2one('product.template', "Operacion", domain=[('categ_id.name','=',OPERACION)])

    @api.model
    def default_get(self, default_fields):
        res = super(calculator_custom_0, self).default_get(default_fields)
        lines = []
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_ENCIMERA, 'display_type': 'line_section', 'name': self.SECTION_ENCIMERA }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_APLACADO, 'display_type': 'line_section', 'name': self.SECTION_APLACADO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_ZOCALO, 'display_type': 'line_section', 'name': self.SECTION_ZOCALO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_CANTO, 'display_type': 'line_section', 'name': self.SECTION_CANTO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_SERVICIO, 'display_type': 'line_section', 'name': self.SECTION_SERVICIO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_OPERACION, 'display_type': 'line_section', 'name': self.SECTION_OPERACION }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_DESCUENTOS, 'display_type': 'line_section', 'name': self.SECTION_DESCUENTOS }])
        res.update({'order_line': lines })

        return res

    @api.onchange('x_studio_oportunidad')
    def _onchange_x_studio_oportunidad(self):
        if(self.partner_id.id == self.x_studio_oportunidad.partner_id.id):
            addr = self.partner_id.address_get(['delivery', 'invoice'])
            self.partner_shipping_id = self.x_studio_oportunidad.x_studio_direccin_de_envo and self.x_studio_oportunidad.x_studio_direccin_de_envo.id or addr['delivery']
        self.partner_id = self.x_studio_oportunidad.partner_id.id
        
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': self.partner_id.x_studio_facturar_a and self.partner_id.x_studio_facturar_a.id or addr['invoice'],
            'partner_shipping_id': self.x_studio_oportunidad.x_studio_direccin_de_envo and self.x_studio_oportunidad.x_studio_direccin_de_envo.id or addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.uid
        if self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        values['team_id'] = self.env['crm.team']._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],user_id=user_id)
        self.update(values)
        
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_DESCUENTOS)

        product_id = self.env['product.template'].search([("name","=",self.PRODUCT_DESCOUNT_NAME)],limit=1)
        # Add or Update line
        if(product_id and self.order_line):
            self.add_update_line(product_id.id, self.SECTION_DESCUENTOS, False, True, self.partner_id.x_studio_descuento_comercial)

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        for rec in self:
            data_encimera = self._get_product_ids_by_category(rec.pricelist_id.id, self.ENCIMERA)
            data_aplacado = self._get_product_ids_by_category(rec.pricelist_id.id, self.APLACADO)
            data_servicio = self._get_product_ids_by_category(rec.pricelist_id.id, self.SERVICIO)
            data_zocalo = self._get_product_ids_by_category(rec.pricelist_id.id, self.ZOCALO)
            data_canto = self._get_product_ids_by_category(rec.pricelist_id.id, self.CANTO)
            data_operacion = self._get_product_ids_by_category(rec.pricelist_id.id, self.OPERACION)

            return {
                'domain': { 
                    'custom_encimera': [('categ_id.name','=',self.ENCIMERA),('id','in',data_encimera)],
                    'custom_encimera2': [('categ_id.name','=',self.ENCIMERA),('id','in',data_encimera)],
                    'custom_aplacado': [('categ_id.name','=',self.APLACADO),('id','in',data_aplacado)],
                    'custom_servicio': [('categ_id.name','=',self.SERVICIO),('id','in',data_servicio)],
                    'custom_zocalo': [('categ_id.name','=',self.ZOCALO),('id','in',data_zocalo)],
                    'custom_canto': [('categ_id.name','=',self.CANTO),('id','in',data_canto)],
                    'custom_operacion': [('categ_id.name','=',self.OPERACION),('id','in',data_operacion)]
                    }
                }

    def _get_product_ids_by_category(self, pricelist_id, category):
        to_return = []
        data = self.env['product.pricelist.item'].search(\
            [('pricelist_id','=',pricelist_id),('product_tmpl_id.categ_id.name','=', category)])
        if(data):
            for product_list in data:
                to_return.append(product_list.product_tmpl_id.id)
        return to_return    

    @api.onchange('custom_encimera')
    def _onchange_custom_encimera(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_ENCIMERA)
            
            # Add or Update line
            if(self.custom_encimera and self.order_line):
                self.add_update_line(self.custom_encimera.id, self.SECTION_ENCIMERA, self.ENCIMERA)

    @api.onchange('custom_encimera2')
    def _onchange_custom_encimera2(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_ENCIMERA)
            
            # Add or Update line
            if(self.custom_encimera2 and self.order_line):
                self.add_update_line(self.custom_encimera2.id, self.SECTION_ENCIMERA, self.ENCIMERA2)

    @api.onchange('custom_aplacado')
    def _onchange_custom_aplacado(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_APLACADO)
            
            # Add or Update line
            if(self.custom_aplacado and self.order_line):
                self.add_update_line(self.custom_aplacado.id, self.SECTION_APLACADO, self.APLACADO)

    @api.onchange('custom_servicio')
    def _onchange_custom_servicio(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_SERVICIO)
            
            # Add or Update line
            if(self.custom_servicio and self.order_line):
                self.add_update_line(self.custom_servicio.id, self.SECTION_SERVICIO, self.SERVICIO)

    @api.onchange('custom_zocalo')
    def _onchange_custom_zocalo(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_ZOCALO)
            
            # Add or Update line
            if(self.custom_zocalo and self.order_line):
                self.add_update_line(self.custom_zocalo.id, self.SECTION_ZOCALO, self.ZOCALO)

    @api.onchange('custom_canto')
    def _onchange_custom_canto(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_CANTO)
            
            # Add or Update line
            if(self.custom_canto and self.order_line):
                self.add_update_line(self.custom_canto.id, self.SECTION_CANTO, self.CANTO)

    @api.onchange('custom_operacion')
    def _onchange_custom_operacion(self):
        if(self._context.get('from_button', False)):
            # Create Seccion if not exists
            self.create_section_in_order_line(self.SECTION_OPERACION)
            
            # Add or Update line
            if(self.custom_operacion and self.order_line):
                self.add_update_line(self.custom_operacion.id, self.SECTION_OPERACION, self.OPERACION)



    def exists_section_in_order_line(self, _type, _name):
        exist = False
        if(self.order_line):
            for _line in self.order_line:
                if(_line.display_type == _type and _line.name == _name):
                    exist = True
        return exist

    def create_section_in_order_line(self, selection_text):
        # Get Or Create Seccion
        exist_section = self.exists_section_in_order_line('line_section', selection_text)
        if(exist_section == False):
            lines = []
            vals = {
                'display_type': 'line_section',
                'name': selection_text,
            }
            lines.append([0,0,vals])
            self.order_line = lines        

    def exists_product_in_order_line(self, _product_id, selection_text):
        is_section = False
        exist = False
        if(self.order_line):
            for _line in self.order_line:
                if(is_section == False and _line.name == selection_text and _line.display_type == 'line_section'):
                    is_section = True
                if(is_section == True):
                    if(_line.product_id.id == _product_id):
                        exist = True
        return exist

    def create_product_in_order_line(self, seccion_text):
        lines = []
        pos_created = -1
        is_in_section = False
        for pos in range(len(self.order_line)):
            lines.append({ 
                'product_id': self.order_line[pos].product_id.id or False,
                'name': self.order_line[pos].name,
                'tax_id': self.order_line[pos].tax_id,
                'display_type': self.order_line[pos].display_type or False,
                'product_uom_qty': self.order_line[pos].product_uom_qty,
                'product_uom': self.order_line[pos].product_uom,
                'x_studio_tablas': self.order_line[pos].x_studio_tablas,
                'x_studio_unidades': self.order_line[pos].x_studio_unidades,
                'x_studio_largo_cm_1': self.order_line[pos].x_studio_largo_cm_1,
                'x_studio_ancho_cm': self.order_line[pos].x_studio_ancho_cm,
                'discount': self.order_line[pos].discount,
                'price_unit': self.order_line[pos].price_unit,
                'price_subtotal': self.order_line[pos].price_subtotal
                })
            if(self.order_line[pos].display_type == 'line_section' and self.order_line[pos].name == seccion_text):
                is_in_section = True
            
            if(is_in_section):
                if(len(self.order_line) == (pos + 1) or self.order_line[pos+1].display_type == 'line_section'):
                    pos_created = pos
                    lines.append({
                        'product_id': False,
                        'name': False,
                        'tax_id': False,
                        'display_type': False,
                        'product_uom_qty': 0,
                        'product_uom': False,
                        'x_studio_unidades': 0,
                        'x_studio_largo_cm_1': 0,
                        'x_studio_ancho_cm': 0,
                        'discount': 0,
                        'price_unit': 0,
                        'price_subtotal': 0
                        })
                    is_in_section = False

        self.order_line = [(5,0,0)]
        for _line in lines:
            self.order_line = [(0,0,_line)]
        
        return pos_created

    def add_update_line(self, selection_id, section_text, category_name=False, is_discount=False, discount=False):
        pos_new_record = -1
        if(is_discount):
            exist_product = self.exists_product_in_order_line(selection_id, section_text)
            if(exist_product == 0):
                pos_new_record = self.create_product_in_order_line(section_text) + 1
            else:
                for line in self.order_line:
                    if(line.product_id.id == selection_id and line.product_id.name == self.PRODUCT_DESCOUNT_NAME):
                        line.update({'name': line.product_id.name + " " + str(discount) + "%"})
                        return
        else:
            pos_new_record = self.create_product_in_order_line(section_text) + 1

        self.order_line[pos_new_record].product_id = selection_id
        self.order_line[pos_new_record].product_id_change()
        custom_name = False
        product_price = self.env['product.pricelist.item'].search([('pricelist_id','=',self.pricelist_id.id),('product_tmpl_id.categ_id.name','=',category_name),('product_tmpl_id.id','=',selection_id)], limit=1)
        if(product_price.x_studio_referencia_scliente and product_price.x_studio_descrip_scliente):
            custom_name = '%s%s' % (product_price.x_studio_referencia_scliente and '[%s] ' % product_price.x_studio_referencia_scliente or '', product_price.x_studio_descrip_scliente)
        if custom_name:
            self.order_line[pos_new_record].name = custom_name
        else:
            self.order_line[pos_new_record].name = self.order_line[pos_new_record].product_id.name
        self.order_line[pos_new_record].price_unit = product_price.fixed_price

        if(self.order_line[pos_new_record].product_id.name == self.PRODUCT_DESCOUNT_NAME):
            self.order_line[pos_new_record].name = self.order_line[pos_new_record].product_id.name + " " + str(discount) + "%"
            self.order_line[pos_new_record].discount = 0


    @api.model
    def create(self, vals):
        vals['custom_encimera'] = False
        vals['custom_encimera2'] = False
        vals['custom_aplacado'] = False
        vals['custom_servicio'] = False
        vals['custom_zocalo'] = False
        vals['custom_canto'] = False
        vals['custom_operacion'] = False
        main_line_remove = []

        # Check If exist another cliente
        clients = []
        clients.append(vals.get('partner_id'))
        if(vals['order_line']):
            for line in vals['order_line']:
                if(line[2]['product_id']):
                    data = self.env['product.pricelist.item'].search(\
                        [('pricelist_id','=',vals['pricelist_id']),('product_tmpl_id','=', line[2]['product_id'])])
                    if(data):
                        for product_list_item in data:
                            if(product_list_item.x_studio_presupuestar_a):
                                if(product_list_item.x_studio_presupuestar_a.id not in clients):
                                    clients.append(product_list_item.x_studio_presupuestar_a.id)

        # save custom
        for client in clients:
            _record_vals = copy.deepcopy(vals)

            if(client != _record_vals['partner_id']):
                _record_vals['partner_id'] = client
                client_data = self.env['res.partner'].search([('id','=',client)], limit=1)
                if(client_data):
                    addr = client_data.address_get(['delivery', 'invoice'])
                    _record_vals['partner_invoice_id'] = addr['invoice']
                

                if _record_vals.get('name', _('New')) == _('New'):
                    seq_date = None
                if 'date_order' in _record_vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(_record_vals['date_order']))
                if 'company_id' in _record_vals:
                    _record_vals['name'] = self.env['ir.sequence'].with_context(force_company=_record_vals['company_id']).next_by_code(
                        'sale.order', sequence_date=seq_date) or _('New')
                else:
                    _record_vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')

                # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
                if any(f not in _record_vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
                    partner = self.env['res.partner'].browse(client)
                    addr = partner.address_get(['delivery', 'invoice'])
                    _record_vals['partner_invoice_id'] = _record_vals.setdefault('partner_invoice_id', addr['invoice'])
                    _record_vals['partner_shipping_id'] = _record_vals.setdefault('partner_shipping_id', addr['delivery'])
                    _record_vals['pricelist_id'] = _record_vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)

                # Update Price and remove line
                line_remove = []
                for i in range(len(_record_vals['order_line'])):
                    product_id = _record_vals['order_line'][i][2]['product_id']
                    if(product_id):
                        data = self.env['product.pricelist.item'].search(\
                            [('pricelist_id','=',vals['pricelist_id']),('product_tmpl_id','=',product_id),('x_studio_presupuestar_a','=',client)], limit=1)
                        if(data):
                            _record_vals['order_line'][i][2]['price_unit'] = data.fixed_price
                            main_line_remove.append(i)
                        else:
                            line_remove.append(i)
                line_remove.reverse()
                for i in line_remove:
                    del _record_vals['order_line'][i]
                super(calculator_custom_0, self).create(_record_vals)

        #save principal
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)

        main_line_remove.reverse()
        for i in main_line_remove:
            del vals['order_line'][i]

        result = super(calculator_custom_0, self).create(vals)
        return result

    @api.onchange('order_line')
    def _onchange_order_line_subtotal(self):
        _subtotal = 0
        _is_section_descount = False

        items = []
        section_now = ""
        for line in self.order_line:
            # Calcula el precio de descuento
            if(line.display_type == 'line_section' and line.name == self.SECTION_DESCUENTOS):
                _is_section_descount = True
            if not _is_section_descount:
                _subtotal += abs(line.price_subtotal)
            if _is_section_descount:
                if(line.product_id.name == self.PRODUCT_DESCOUNT_NAME):
                    if(self.partner_id):
                        price_discount = (_subtotal * self.partner_id.x_studio_descuento_comercial)/100
                        line.update({'price_unit': price_discount*(-1)})

            # PRODUCT_MERMA_NAME
            if(_is_section_descount == False):
                
                if(line.display_type == 'line_section'):
                    section_now = line.name

                if(line.product_id.id != False and line.product_id.id != self.PRODUCT_MERMA_ID and line.display_type == False):
                    _pos = -1
                    _m2t = line.x_studio_tablas * (line.product_id.x_studio_largo_cm/100) * (line.product_id.x_studio_alto_cm/100)
                    for pos in range(len(items)):
                        if(items[pos]['product_id'] == line.product_id.id):
                            _pos = pos
                            break

                    if(int(_pos) == int(-1)):
                        items.append({
                            'product_id': line.product_id.id,
                            'product_name': line.product_id.name, 
                            'tablas': line.x_studio_tablas, 
                            'm2t': _m2t, 
                            'm2u': line.product_uom_qty, 
                            'price': line.product_id.standard_price,
                            'section': section_now
                            })
                    else:
                        items[_pos]['tablas'] = line.x_studio_tablas + items[_pos]['tablas']
                        items[_pos]['m2t'] = _m2t + items[_pos]['m2t']
                        items[_pos]['m2u'] = line.product_uom_qty + items[_pos]['m2u']
                        items[_pos]['m2t'] = _m2t + items[_pos]['m2t']
                        items[_pos]['section'] = section_now

        for merma in items:
            if(merma['tablas'] > 0):
                pos_new_record = self.check_if_exists_merma_product(self.PRODUCT_MERMA_ID, merma['product_name'])
                if(int(pos_new_record) == int(-1)):
                    pos_new_record = self.create_product_in_order_line(merma['section']) + 1
                    self.order_line[pos_new_record].product_id = self.PRODUCT_MERMA_ID
                    self.order_line[pos_new_record].product_id_change()
                self.order_line[pos_new_record].name = self.PRODUCT_MERMA_NAME + ": " + merma['product_name']
                self.order_line[pos_new_record].product_uom_qty = merma['m2t'] - merma['m2u']
                self.order_line[pos_new_record].price_unit = merma['price']
                    
    def check_if_exists_merma_product(self, merma_id, product_name):
        pos_found = -1
        if(self.order_line):
            for pos in range(len(self.order_line)):
                description_name = self.PRODUCT_MERMA_NAME + ": " + product_name
                if(self.order_line[pos].product_id.id == merma_id and self.order_line[pos].name == description_name):
                    pos_found = pos
                    break
        return pos_found
    



class calculator_custom_1(models.Model):

    _inherit = 'sale.order.line'
    
    report_product_description = field_name = fields.Text(string='Descripción', compute='_get_report_product_description')
    
    @api.onchange('x_studio_unidades', 'x_studio_largo_cm_1', 'x_studio_ancho_cm')
    def _onchange_area(self):
        for line in self:
            if(line.x_studio_largo_cm_1 == 0 or line.x_studio_ancho_cm == 0):
                line.product_uom_qty = line.x_studio_unidades
            elif((line.x_studio_largo_cm_1 * line.x_studio_ancho_cm) != 0):
                line.product_uom_qty = (line.x_studio_largo_cm_1 * line.x_studio_ancho_cm)

    def _get_report_product_description(self):
        for record in self:
            data = self.env['product.pricelist.item'].search([('pricelist_id','=',record.order_id.pricelist_id.id),('product_tmpl_id','=', record.product_template_id.id)], limit=1)
            if(data):
                text = ""
                if(data.x_studio_referencia_scliente):
                    text = "[" + data.x_studio_referencia_scliente + "]"
                if(data.x_studio_descrip_scliente):
                    text = data.x_studio_descrip_scliente
                report_product_description = ""
            else:
                report_product_description = record.name
            
        
    # @api.onchange('x_studio_tablas','x_studio_largo_cm_1','x_studio_ancho_cm','product_uom_qty')
    # def _onchange_mermas(self):
    #     test = ""