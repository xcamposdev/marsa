# -*- coding: utf-8 -*-

import logging
from odoo import tools
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class custom_report_list_iva(models.Model):
    
    _inherit = "purchase.report"

    industry_id = fields.Many2one('res.partner.industry', 'Sector', readonly=True)

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
                SELECT
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    po.currency_id,
                    t.uom_id as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_total,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                    sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
                    sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                    sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                    sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                         else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                    end as qty_to_be_billed, 
                    min(partner.industry_id) as industry_id
        """ % self.env['res.currency']._select_companies_rates()
        return select_str
