# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions

_logger = logging.getLogger(__name__)


class calculator_custom_0(models.Model):
    
    _inherit = 'sale.order'

    def _get_product_encimera(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    def _get_product_aplacado(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    def _get_product_servicio(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    def _get_product_zocalo(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    def _get_product_canto(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    def _get_product_operacion(self):
        products = self.env['product.template'].search([('categ_id.name','=','OPS Encimera - Aplacado')])
        lst = []
        if(products):
            for product in products:
                lst.append((product.id, product.name))
        return lst
    
    #x_studio_encimera = fields.Selection(_get_product_encimera)
    #x_studio_aplacado = fields.Selection(_get_product_aplacado)
    #x_studio_servicio = fields.Selection(_get_product_servicio)
    #x_studio_zocalo = fields.Selection(_get_product_zocalo)
    #x_studio_canto = fields.Selection(_get_product_canto)
    #x_studio_operacion = fields.Selection(_get_product_operacion)
    
      
    
    @api.onchange('x_studio_oportunidad')
    def _onchange_x_studio_oportunidad(self):
        self.partner_id = self.x_studio_oportunidad.partner_id
