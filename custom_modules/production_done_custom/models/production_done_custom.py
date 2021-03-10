# -*- coding: utf-8 -*-
import warnings
import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError


_logger = logging.getLogger(__name__)

class production_done_custom(models.Model):

    _inherit = "mrp.production"
    
    def button_mark_done(self):
        res = super(production_done_custom, self).button_mark_done()

        if res == True and self.state == 'done' and self.origin:
            sale_order = self.env['sale.order'].search([('name','=',self.origin)])
            if sale_order:
                sale_order_name = self.get_sale_name_by_oportunity(sale_order.x_studio_oportunidad)
                productions = self.env['mrp.production'].search([('origin','in',sale_order_name),('x_opportunity_prod','=',sale_order.x_studio_oportunidad.name)])
                done_or_cancel = list(data for data in productions if data.state == 'done' or data.state == 'cancel')
                if len(productions) == len(done_or_cancel):
                    stage_previous_name = self.env['ir.config_parameter'].sudo().get_param('x_crm_etapa_anterior_producida')
                    stage_name = self.env['ir.config_parameter'].sudo().get_param('x_crm_etapa_producida')
                    stage_previous = self.env['crm.stage'].search([('name','=',stage_previous_name)])
                    stage = self.env['crm.stage'].search([('name','=',stage_name)])

                    crm = self.env['crm.lead'].search([('id','=',sale_order.x_studio_oportunidad.id)])
                    if crm and crm.stage_id.id == stage_previous.id:
                        crm.write({ 'stage_id': stage.id })
                #* Borrador: El MO aún no está confirmado.
                #* Confirmado: El MO está confirmado, las reglas de stock y el reordenamiento de los componentes se gestionan.
                #* Planificado: Los WO están planificados.
                #* En curso: la producción ha comenzado (en el MO o en el WO).
                #* Para cerrar: La producción está hecha, el MO tiene que estar cerrado.
                #* Hecho: el MO está cerrado, los movimientos de acciones se registran.
                #* Cancelado: el MO ha sido cancelado, ya no se puede confirmar.
        return res

    def get_sale_name_by_oportunity(self, opportunity):
        sale_order_names = []
        for order in opportunity.order_ids:
            if order.state in ['sale','done']:
                data_find = list(_data for _data in sale_order_names if _data == order.name)
                if not data_find:
                    sale_order_names.append(order.name)
        
        sales = self.env['sale.order'].search([('x_studio_oportunidad','=',opportunity.id)])
        for order in sales:
            if order.state in ['sale','done']:
                data_find = list(_data for _data in sale_order_names if _data == order.name)
                if not data_find:
                    sale_order_names.append(order.name)
        return sale_order_names