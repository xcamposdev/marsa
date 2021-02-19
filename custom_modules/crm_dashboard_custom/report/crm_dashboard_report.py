# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

from functools import lru_cache


class crm_dashboard_report(models.Model):
    _name = "crm.dashboard.report"
    _description = "crm dashboard report"
    _auto = False
    _rec_name = 'x_create_date'
    _order = 'x_create_date desc'

    x_create_date = fields.Date(string='Fecha de Creación', readonly=True)
    x_crm_quantity = fields.Integer(string="Ventas", readonly=True)
    x_measurements = fields.Integer(string="Mediciones", readonly=True)
    x_production = fields.Integer(string="Pasadas a Taller", readonly=True)
    x_mounting = fields.Integer(string='Montadas', readonly=True)
    x_finished = fields.Integer(string='Ventas Finalizadas', readonly=True)
    x_difference = fields.Integer(string='Diferencia', readonly=True)

    @api.model
    def _query(self):
        op_measurement_old = self.env['ir.config_parameter'].sudo().get_param('x_op_measurement_old')
        op_measurement_new = self.env['ir.config_parameter'].sudo().get_param('x_op_measurement_new')
        op_production_new = self.env['ir.config_parameter'].sudo().get_param('x_op_production_new')
        op_mounting_old = self.env['ir.config_parameter'].sudo().get_param('x_op_mounting_old')
        op_mounting_new = self.env['ir.config_parameter'].sudo().get_param('x_op_mounting_new')
        op_finished_new = self.env['ir.config_parameter'].sudo().get_param('x_op_finished_new')

        return '''
            SELECT ROW_NUMBER() OVER (order by x_crm_id) as id, x_create_date, 1 as x_crm_quantity,
                    CASE WHEN sum(x_measurements) > 0 THEN 1 ELSE 0 END as x_measurements,
                    CASE WHEN sum(x_production)>0 THEN 1 ELSE 0 END as x_production,
                    CASE WHEN sum(x_mounting)>0 THEN 1 ELSE 0 END as x_mounting,
                    CASE WHEN sum(x_finished)>0 THEN 1 ELSE 0 END as x_finished,
                    CASE WHEN sum(x_finished)>0 THEN 0 ELSE 1 END as x_difference
            FROM (
                SELECT crm.id as x_crm_id, crm.create_date as x_create_date, 1 as x_crm_quantity, 
                    CASE WHEN mtv.old_value_char='%s' and mtv.new_value_char='%s' THEN 1 ELSE 0 END as x_measurements,
                    CASE WHEN mtv.new_value_char='%s' THEN 1 ELSE 0 END as x_production,
                    CASE WHEN mtv.old_value_char='%s' and mtv.new_value_char='%s' THEN 1 ELSE 0 END as x_mounting,
                    CASE WHEN mtv.new_value_char='%s' THEN 1 ELSE 0 END as x_finished,
                    --COUNT(*) FILTER (WHERE mtv.old_value_char='Medición' and mtv.new_value_char='Presupuesto teorico') as x_measurements,
                    mtv.old_value_char, mtv.new_value_char
                    
                FROM crm_lead crm INNER JOIN mail_message mm ON crm.id=mm.res_id and mm.model='crm.lead'
                                INNER JOIN mail_tracking_value mtv ON mm.id=mtv.mail_message_id and mtv.field='stage_id'
                WHERE crm.active=true
                ) a 
            GROUP BY x_crm_id, x_create_date
        ''' % (op_measurement_old, op_measurement_new, op_production_new, op_mounting_old, op_mounting_new, op_finished_new)

  
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        ''' % (
            self._table, self._query()
        ))
