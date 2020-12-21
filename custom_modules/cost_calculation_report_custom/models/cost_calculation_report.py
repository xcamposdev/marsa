# -*- coding: utf-8 -*-

import logging
import copy
import math
from itertools import groupby
from decimal import Decimal
from datetime import timedelta
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from datetime import datetime

_logger = logging.getLogger(__name__)

class cost_calculation_report_custom(models.Model):
    
    _inherit = 'purchase.order'

    
    def get_lines_custom(self):
        to_return = []
        for record in self:
            if(record.origin):
                origins = list(record.origin.split(","))
                for origin in origins:
                    sale_order = self.env['sale.order'].search([('name','=',origin)])
                    if sale_order and sale_order.x_studio_oportunidad:
                        if(sale_order.x_studio_medidor and sale_order.x_studio_montador and sale_order.x_studio_medidor == sale_order.x_studio_montador):
                            self.addLine_custom(sale_order, "medidor", record, to_return)
                        else:
                            if sale_order.x_studio_medidor:
                                self.addLine_custom(sale_order, "medidor", record, to_return)
                            if sale_order.x_studio_montador:
                                self.addLine_custom(sale_order, "montador", record, to_return)
        
        return to_return

    def addLine_custom(self, sale_order, type, record, to_return):
        if type == "medidor":
            data_find = list(_data for _data in to_return if _data['partner_id'] == sale_order.x_studio_medidor.id)
            contact = sale_order.x_studio_medidor
        if type == "montador":
            data_find = list(_data for _data in to_return if _data['partner_id'] == sale_order.x_studio_montador.id)
            contact = sale_order.x_studio_montador
        if not data_find:
            data_find = {
                'partner_id': contact.id,
                'name': contact.name,
                'total': 0,
                'purchase': []
            }
            to_return.append(data_find)
        else: 
            data_find = data_find[0]
        
        data_order = {
            'sale_date_order': sale_order.date_order.strftime('%d/%m/%Y'),
            'purchase_date_order': record.date_order.strftime('%d/%m/%Y'),
            'oportunidad': sale_order.x_studio_oportunidad.name if sale_order.x_studio_oportunidad else '',
            'importe': record.amount_total,
            'purchase_order_line': []
        }
        detail = []
        for line in record.order_line:
            if line.display_type == False:
                detail.append({
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price': line.price_unit,
                    'price_subtotal': line.price_unit,
                })
        
        data_order['purchase_order_line'] = detail
        data_find['purchase'].append(data_order)
        data_find['total'] = data_find['total'] + record.amount_total
        