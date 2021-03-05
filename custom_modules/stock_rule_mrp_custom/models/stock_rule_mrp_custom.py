# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class stock_rule_mrp_custom(models.Model):

    _inherit = 'stock.rule'

    @api.model
    def _run_manufacture(self, procurements):
        productions_values_by_company = defaultdict(list)
        for procurement, rule in procurements:
            bom = self._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)
            if not bom:
                msg = _('There is no Bill of Material of type manufacture or kit found for the product %s. Please define a Bill of Material for this product.') % (procurement.product_id.display_name,)
                raise UserError(msg)

            #####################
            sale = self.env['sale.order'].search([('name','=',procurement.origin)])
            if sale:
                data = list(_data for _data in productions_values_by_company[procurement.company_id.id] \
                    if _data['product_id'] == procurement.product_id.id and procurement.origin in _data['origin'])
                if data:
                    data[0]['product_qty'] = float(data[0]['product_qty']) + float(procurement.product_qty)
                else:
                    productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))
            else:
                productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))
            #####################

            #productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))

        for company_id, productions_values in productions_values_by_company.items():
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            productions = self.env['mrp.production'].sudo().with_context(force_company=company_id).create(productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            productions.action_confirm()

            for production in productions:
                origin_production = production.move_dest_ids and production.move_dest_ids[0].raw_material_production_id or False
                orderpoint = production.orderpoint_id
                if orderpoint:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': orderpoint},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
                if origin_production:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': origin_production},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
        return True