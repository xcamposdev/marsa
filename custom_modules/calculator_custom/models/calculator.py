# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions

_logger = logging.getLogger(__name__)


class calculator_custom_0(models.Model):
    
    _inherit = 'sale.order'

    ENCIMERA = "Encimera"
    APLACADO = "Aplacado"
    SERVICIO = "Servicio"
    ZOCALO = "Zocalo"
    CANTO = "Canto"
    OPERACION = "Operacion"

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
    
      
    # @api.onchange('x_studio_oportunidad')
    # def _onchange_x_studio_oportunidad(self):
    #     self.partner_id = self.x_studio_oportunidad.partner_id

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

    @api.onchange('custom_encimera')
    def _onchange_custom_encimera(self):
        # Get Or Create Seccion
        exist_section = self.exists_section_in_order_line('line_section', self.SECTION_ENCIMERA)
        if(exist_section == False):
            lines = []
            vals = {
                'display_name': 'Nuevo - ' + self.SECTION_ENCIMERA,
                'display_type': 'line_section',
                'name': self.SECTION_ENCIMERA,
            }
            lines.append([0,0,vals])
            self.order_line = lines
        
        # Add line
        exist_product = self.exists_product_in_order_line(self.SECTION_ENCIMERA)
        if(self.order_line):
            lines = []
            for line in self.order_line:
                # lines.append([0,0,line])
                if(exist_product):
                    te=""
                    # search_var = self.search([('staff_age','=',0)])
                    # search_var.write({ 
                    #     'stud_ids': [(0,0, {'reg_no':4200,'stud_email':'anbulove@gmail.com','stud_phone':'9788987689'})]
                else:
                    if(line.display_type == 'line_section' and line.name == self.SECTION_ENCIMERA):
                        vals = {
                            'product_id': self.custom_encimera.id,
                            'product_uom_qty': 1,
                        }
                        lines.append([0,0,vals])
            self.order_line = lines

    def exists_section_in_order_line(self, _type, _name):        
        exist = False
        if(self.order_line):
            for _line in self.order_line:
                if(_line.display_type == _type and _line.name == _name):
                    exist = True
        return exist

    def exists_product_in_order_line(self, _product_id):        
        exist = False
        if(self.order_line):
            for _line in self.order_line:
                if(_line.product_id == _product_id):
                    exist = True
        return exist

    # SECTION_ENCIMERA = "Seccion Encimera"
    # SECTION_APLACADO = "Seccion Aplacado"
    # SECTION_SERVICIO = "Seccion Servicio"
    # SECTION_ZOCALO = "Seccion Zocalo"
    # SECTION_CANTO = "Seccion Canto"
    # SECTION_OPERACION = "Seccion Operacion"

        

    @api.onchange('custom_aplacado')
    def _onchange_custom_aplacado(self):
        test = ""

    @api.onchange('custom_servicio')
    def _onchange_custom_servicio(self):
        test = ""

    @api.onchange('custom_zocalo')
    def _onchange_custom_zocalo(self):
        test = ""

    @api.onchange('custom_canto')
    def _onchange_custom_canto(self):
        test = ""

    @api.onchange('custom_operacion')
    def _onchange_custom_operacion(self):
        test = ""
    