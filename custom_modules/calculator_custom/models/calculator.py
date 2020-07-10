# -*- coding: utf-8 -*-

import logging
import copy
from decimal import Decimal
from odoo import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class calculator_custom_0(models.Model):
    
    _inherit = 'sale.order'

    ENCIMERA = "Material"
    APLACADO = "Material"
    SERVICIO = "Servicio"
    ZOCALO = "Material"
    CANTO = "Canto"
    OPERACION = "Operaciones"

    SECTION_ENCIMERA = "Seccion Encimera"
    SECTION_APLACADO = "Seccion Aplacado"
    SECTION_SERVICIO = "Seccion Servicio"
    SECTION_ZOCALO = "Seccion Zocalo"
    SECTION_CANTO = "Seccion Canto"
    SECTION_OPERACION = "Seccion Operacion"
    
    custom_encimera = fields.Many2one('product.template', "Encimera", domain=[('categ_id.name','=',ENCIMERA)])
    custom_aplacado = fields.Many2one('product.template', "Aplacado", domain=[('categ_id.name','=',APLACADO)])
    custom_servicio = fields.Many2one('product.template', "Servicio", domain=[('categ_id.name','=',SERVICIO)])
    custom_zocalo = fields.Many2one('product.template', "Zocalo", domain=[('categ_id.name','=',ZOCALO)])
    custom_canto = fields.Many2one('product.template', "Canto", domain=[('categ_id.name','=',CANTO)])
    custom_operacion = fields.Many2one('product.template', "Operacion", domain=[('categ_id.name','=',OPERACION)])
    
      
    @api.onchange('x_studio_oportunidad')
    def _onchange_x_studio_oportunidad(self):
        self.partner_id = self.x_studio_oportunidad.partner_id
        #self.partner_shipping_id = self.x_studio_oportunidad.x_studio_direccin_de_envo.id
        
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

    @api.model
    def default_get(self, default_fields):
        res = super(calculator_custom_0, self).default_get(default_fields)
        lines = []
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_ENCIMERA, 'display_type': 'line_section', 'name': self.SECTION_ENCIMERA }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_APLACADO, 'display_type': 'line_section', 'name': self.SECTION_APLACADO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_SERVICIO, 'display_type': 'line_section', 'name': self.SECTION_SERVICIO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_ZOCALO, 'display_type': 'line_section', 'name': self.SECTION_ZOCALO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_CANTO, 'display_type': 'line_section', 'name': self.SECTION_CANTO }])
        lines.append([0,0,{ 'display_name': 'Nuevo - ' + self.SECTION_OPERACION, 'display_type': 'line_section', 'name': self.SECTION_OPERACION }])
        res.update({'order_line': lines })
        return res

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

    def add_update_line(self, selection_id, selection_text):
        exist_product = self.exists_product_in_order_line(selection_id, selection_text)
        lines = []
        is_created = exist_product
        pos = 0
        pos_new_record = 0
        for line in self.order_line:
            pos = pos + 1
            lines.append({ 
                'product_id': line.product_id.id or False,
                'name': line.name,
                'tax_id': line.tax_id,
                'display_type': line.display_type or False,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom,
                'x_studio_unidades': line.x_studio_unidades,
                'x_studio_largo_cm_1': line.x_studio_largo_cm_1,
                'x_studio_ancho_cm': line.x_studio_ancho_cm,
                'discount': line.discount,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal
                })
            if(is_created == False and line.display_type == 'line_section' and line.name == selection_text):
                pos_new_record = pos
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
                is_created = True

        self.order_line = [(5,0,0)]
        for _line in lines:
            self.order_line = [(0,0,_line)]
        
        if(not exist_product):
            self.order_line[pos_new_record].product_id = selection_id
            self.order_line[pos_new_record].product_id_change()
        else:
            for line in self.order_line:
                if(line.product_id.id == selection_id):
                    quantity = line.product_uom_qty + 1
                    line.update({'product_uom_qty': quantity})

    
        
    @api.onchange('custom_encimera')
    def _onchange_custom_encimera(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_ENCIMERA)
        
        # Add or Update line
        if(self.custom_encimera and self.order_line):
            self.add_update_line(self.custom_encimera.id, self.SECTION_ENCIMERA)



    @api.onchange('custom_aplacado')
    def _onchange_custom_aplacado(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_APLACADO)
        
        # Add or Update line
        if(self.custom_aplacado and self.order_line):
            self.add_update_line(self.custom_aplacado.id, self.SECTION_APLACADO)

    @api.onchange('custom_servicio')
    def _onchange_custom_servicio(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_SERVICIO)
        
        # Add or Update line
        if(self.custom_servicio and self.order_line):
            self.add_update_line(self.custom_servicio.id, self.SECTION_SERVICIO)

    @api.onchange('custom_zocalo')
    def _onchange_custom_zocalo(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_ZOCALO)
        
        # Add or Update line
        if(self.custom_zocalo and self.order_line):
            self.add_update_line(self.custom_zocalo.id, self.SECTION_ZOCALO)

    @api.onchange('custom_canto')
    def _onchange_custom_canto(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_CANTO)
        
        # Add or Update line
        if(self.custom_canto and self.order_line):
            self.add_update_line(self.custom_canto.id, self.SECTION_CANTO)

    @api.onchange('custom_operacion')
    def _onchange_custom_operacion(self):
        # Create Seccion if not exists
        self.create_section_in_order_line(self.SECTION_OPERACION)
        
        # Add or Update line
        if(self.custom_operacion and self.order_line):
            self.add_update_line(self.custom_operacion.id, self.SECTION_OPERACION)


    @api.model
    def create(self, vals):
        vals['custom_encimera'] = False
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

class calculator_custom_1(models.Model):

    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'x_studio_largo_cm_1', 'x_studio_ancho_cm')
    def _compute_amount(self):
        # res = super(calculator_custom_0, self)._compute_amount()

        # return res
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            quantity_custom = line.product_uom_qty
            if((line.x_studio_largo_cm_1 * line.x_studio_ancho_cm) == 0):
                quantity_custom = line.product_uom_qty
            elif((line.x_studio_largo_cm_1 * line.x_studio_ancho_cm) != 0):
                quantity_custom = (line.x_studio_largo_cm_1 * line.x_studio_ancho_cm * line.product_uom_qty)


            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, quantity_custom, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })