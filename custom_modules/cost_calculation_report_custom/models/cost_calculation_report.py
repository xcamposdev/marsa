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
            oportunidad = ""
            if(record.origin):
                sale_order = self.env['sale.order'].search([('name','=',record.origin)])
                if sale_order and sale_order.x_studio_oportunidad:
                    oportunidad = sale_order.x_studio_oportunidad.name
                else:
                    oportunidad = record.origin
            else:
                oportunidad = record.origin

            data_find = list(_data for _data in to_return if _data['partner_id'] == record.partner_id.id)
            if not data_find:
                data_find = {
                'partner_id': record.partner_id.id,
                'name': record.partner_id.name,
                'total': 0,
                'purchase': [],
                'group': []
                }
                to_return.append(data_find)
            else: 
                data_find = data_find[0]
        
            data_order = {
                'purchase_date_order': record.date_order.strftime('%d/%m/%Y'),
                'oportunidad': oportunidad,
                'importe': record.amount_untaxed,
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
                        'price_subtotal': line.price_subtotal,
                    })
            
            data_order['purchase_order_line'] = detail
            data_find['purchase'].append(data_order)
            data_find['total'] = data_find['total'] + record.amount_untaxed

        return to_return