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

    x_name = fields.Char(string="Oportunidad", readonly=True)
    x_partner_id = fields.Many2one('res.partner', string="Cliente", readonly=True)
    x_create_date = fields.Date(string='Fecha de Creación', readonly=True)
    x_crm_quantity = fields.Integer(string="Ventas", readonly=True)
    x_measurements = fields.Integer(string="Mediciones", readonly=True)
    x_production = fields.Integer(string="Pasadas a Taller", readonly=True)
    x_mounting = fields.Integer(string='Montadas', readonly=True)
    x_finished = fields.Integer(string='Ventas Finalizadas', readonly=True)
    x_difference = fields.Integer(string='Diferencia', readonly=True)
    x_montador = fields.Char(string="Montador", readonly=True)
    x_montador_startdate = fields.Date(string="Fecha Reunion Montador", readonly=True)
    x_medidor = fields.Char(string="Medidor", readonly=True)
    x_medidor_startdate = fields.Date(string="Fecha Reunion Medidor", readonly=True)
    x_categories = fields.Char(string="Categorías", readonly=True, invisible=True)

    @api.model
    def _query(self):
        op_measurement_old = self.env['ir.config_parameter'].sudo().get_param('x_op_measurement_old')
        op_measurement_new = self.env['ir.config_parameter'].sudo().get_param('x_op_measurement_new')
        op_production_new = self.env['ir.config_parameter'].sudo().get_param('x_op_production_new')
        op_mounting_old = self.env['ir.config_parameter'].sudo().get_param('x_op_mounting_old')
        op_mounting_new = self.env['ir.config_parameter'].sudo().get_param('x_op_mounting_new')
        op_finished_new = self.env['ir.config_parameter'].sudo().get_param('x_op_finished_new')

        return '''
            SELECT ROW_NUMBER() OVER (order by x_crm_id) as id, x_name, MIN(x_partner_id) as x_partner_id,
                    x_create_date, Max(x_crm_quantity) as x_crm_quantity,
                    CASE WHEN sum(x_measurements) > 0 THEN 1 ELSE 0 END as x_measurements,
                    CASE WHEN sum(x_production)>0 THEN 1 ELSE 0 END as x_production,
                    CASE WHEN sum(x_mounting)>0 THEN 1 ELSE 0 END as x_mounting,
                    CASE WHEN sum(x_finished)>0 THEN 1 ELSE 0 END as x_finished,
                    CASE WHEN (Max(x_crm_quantity) - (CASE WHEN sum(x_finished)>0 THEN 1 ELSE 0 END)) > 0 THEN (Max(x_crm_quantity) - (CASE WHEN sum(x_finished)>0 THEN 1 ELSE 0 END)) ELSE 0 END as x_difference,
                    ----CASE WHEN sum(x_finished)>0 THEN 0 ELSE 1 END as x_difference,
                    MIN(x_montador) as x_montador, MAX(x_montador_startdate) as x_montador_startdate,
                    MIN(x_medidor) as x_medidor, MAX(x_medidor_startdate) as x_medidor_startdate,
                    STRING_AGG(distinct x_categories,', ') as x_categories
            FROM (
                SELECT crm.id as x_crm_id, crm.name x_name, crm.partner_id x_partner_id, crm.create_date as x_create_date, 
                        --1 as x_crm_quantity, 
                        CASE WHEN mtv.new_value_char in (%s) THEN 1 ELSE 0 END as x_crm_quantity,
                        CASE WHEN mtv.old_value_char in (%s) and mtv.new_value_char in (%s) THEN 1 ELSE 0 END as x_measurements,
                        CASE WHEN mtv.new_value_char in (%s) THEN 1 ELSE 0 END as x_production,
                        CASE WHEN mtv.old_value_char in (%s) and mtv.new_value_char in (%s) THEN 1 ELSE 0 END as x_mounting,
                        CASE WHEN mtv.new_value_char in (%s) THEN 1 ELSE 0 END as x_finished,
                        mtv.old_value_char, mtv.new_value_char,
                        CASE WHEN mtv.old_value_char in (%s) and mtv.new_value_char in (%s) THEN mtv.create_date ELSE null END as x_montador_startdate,
                        CASE WHEN mtv.old_value_char in (%s) and mtv.new_value_char in (%s) THEN mtv.create_date ELSE null END as x_medidor_startdate,
                        reunion.montador as x_montador, reunion.montador_startdate as x_montador_startdate,
                        reunion.medidor as x_medidor, reunion.medidor_startdate as x_medidor_startdate,
                        crm_lt.name as x_categories
                    
                FROM crm_lead crm INNER JOIN mail_message mm ON crm.id=mm.res_id and mm.model='crm.lead'
                                LEFT JOIN mail_tracking_value mtv ON mm.id=mtv.mail_message_id and mtv.field='stage_id'
                                LEFT JOIN (SELECT ce.opportunity_id, 
                                        MIN(r_p.name) FILTER (WHERE x_studio_subtipo='Montador') montador,
                                        MIN(r_p.name) FILTER (WHERE x_studio_subtipo='Medidor') medidor
                                    FROM calendar_event ce INNER JOIN calendar_event_res_partner_rel ce_rel ON ce.id=ce_rel.calendar_event_id
                                                INNER JOIN res_partner r_p ON r_p.id=ce_rel.res_partner_id
                                                INNER JOIN res_users r_u ON r_u.partner_id=r_p.id and (r_u.x_studio_subtipo='Medidor' or r_u.x_studio_subtipo='Montador')
                                    GROUP BY ce.opportunity_id) reunion ON reunion.opportunity_id=crm.id
                                LEFT JOIN crm_lead_tag_rel crm_ltr ON crm_ltr.lead_id = crm.id
                                LEFT JOIN crm_lead_tag crm_lt ON crm_ltr.tag_id=crm_lt.id
            WHERE crm.active=true
            ) a 
            GROUP BY x_crm_id, x_name, x_create_date
        ''' % (op_measurement_old, op_measurement_old, op_measurement_new, op_production_new, op_mounting_old, op_mounting_new, op_finished_new, \
                op_measurement_old, op_measurement_new, op_mounting_old, op_mounting_new)

  
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        ''' % (
            self._table, self._query()
        ))
