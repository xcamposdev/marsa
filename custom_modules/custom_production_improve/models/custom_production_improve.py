# -*- coding: utf-8 -*-
import warnings
import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)

class custom_production_improve(models.Model):

    _inherit = "mrp.production"
    
    x_opportunity_prod = fields.Char(string='Oportunidad', compute="get_production_opportunity")

    # Agregamos una nueva columna 'oportunidad' para mostrar el nombre de la oportunidad
    # al listado de ordenes de produccion.
    def get_production_opportunity(self):
        for record in self:
            if(record.origin):
                sale_order = record.env['sale.order'].search([('name','=',record.origin), ('state', '=', 'sale')])
                if sale_order and sale_order.x_studio_oportunidad.id:
                    record.x_opportunity_prod = sale_order.x_studio_oportunidad.name
                else:
                    record.x_opportunity_prod = False
            else:
                record.x_opportunity_prod = False
    
    # Al crear una nueva orden de produccion adjuntamos los docx con nombre PL_ 
    # obtenidos de la oportunidad en caso de que existan.
    @api.model
    def create(self, values):
        production = super(custom_production_improve, self).create(values)
        
        if(production.origin):
            sale_order = self.env['sale.order'].search([('name','=',production.origin)])
            if sale_order and sale_order.x_studio_oportunidad:
                opportunity = sale_order.x_studio_oportunidad.id

                attachments = self.env['ir.attachment'].search([('res_id','=', opportunity), ('res_model','=', 'crm.lead'), ('name','like', 'PL_')])

                for attach in attachments:
                    self.env['ir.attachment'].create({
                            'name': attach.name,
                            'type': attach.type,
                            'datas': attach.datas,
                            'res_model': 'mrp.production',
                            'res_id': production.id,
                            'mimetype': attach.mimetype
                        })

        return production 
    
class custom_production_stock_available(models.TransientModel):
    
    _inherit = 'mrp.product.produce.line'

    x_total_stock_available = fields.Float(string='Stock disponible', readonly = True, compute="get_stock_available")
    
    @api.depends('lot_id')
    def get_stock_available(self):
        self.x_total_stock_available = 0
        if(self.lot_id):
            self.x_total_stock_available = self.lot_id.product_qty
