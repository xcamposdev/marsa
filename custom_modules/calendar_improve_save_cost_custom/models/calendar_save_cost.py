# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
_logger = logging.getLogger(__name__)


class CalendarImproveSaveCost(models.Model):

    _inherit = 'calendar.event'

    x_has_montador_partner = fields.Boolean(default=True)

    @api.onchange('partner_ids')
    def _get_user_subtype(self):
        self.x_has_montador_partner = False

        if(len(self.partner_ids) > 0):
            for partner in self.partner_ids:
                user_type = self.env['res.users'].search([('partner_id', '=', partner.ids)])
                if user_type.x_studio_subtipo == 'Montador' and self.opportunity_id:
                    self.x_has_montador_partner = True

    def save_cost(self):
        if self.x_has_montador_partner and self.opportunity_id:
            sales_ids = self.get_sale_id_by_oportunity(self.opportunity_id)
            order_sales = self.env['sale.order'].search([('id', 'in', sales_ids)])
            if order_sales:
                for order in order_sales:
                    order.get_obtener_datos()
                    order.save_cost()

    def get_sale_id_by_oportunity(self, opportunity):
        sale_order_ids = []
        for order in opportunity.order_ids:
            if order.state in ['sale','done']:
                data_find = list(data for data in sale_order_ids if data == order.id)
                if not data_find:
                    sale_order_ids.append(order.id)
        
        sales = self.env['sale.order'].search([('x_studio_oportunidad','=',opportunity.id)])
        for order in sales:
            if order.state in ['sale','done']:
                data_find = list(data for data in sale_order_ids if data == order.id)
                if not data_find:
                    sale_order_ids.append(order.id)
        return sale_order_ids
