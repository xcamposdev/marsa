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
import pytz
from datetime import datetime

_logger = logging.getLogger(__name__)

class cost_calculation_custom_0(models.Model):

    _inherit = 'sale.order'

    x_studio_obra = fields.Selection([
        ('si','Si'),
        ('no','No')
        ], string = "Obra", default='no')
    x_studio_coste_medicin = fields.Integer(string = "Coste Medición", default = 0)
    x_studio_coste_montaje = fields.Integer(string = "Coste Montaje", default = 0)

    x_studio_medicin = fields.Selection([
        ('si','Si'),
        ('no','No')
        ], string = "Medición", default='no')
    x_studio_km_medicin = fields.Integer(string = "Km. Medición", default = 0)
    x_studio_coronas_medicin = fields.Integer(string = "Coronas Medición", default = 0, store = True)
    x_studio_2_medicin = fields.Selection([
        ('si','Si'),
        ('no','No')
        ], string = "2ª Medición", default='no')

    x_studio_montaje = fields.Selection([
        ('si','Si'),
        ('no','No'),
        ('incidencia','Incidencia')
        ], string = "Montaje", default='no')
    x_studio_km_montaje = fields.Integer(string = "Km. Montaje", default = 0)
    x_studio_coronas_montaje = fields.Integer(string = "Coronas Montaje", default = 0, store = True)
    x_studio_instalacin_extra = fields.Integer(string = "Instalación Extra", default = 0)
    x_studio_colocacin_aplacados = fields.Float(string = "Colocación Aplacados", default = 0.0)
    x_studio_medir_aplacados = fields.Integer(string = "Medir Aplacados", default = 0, store = True)
    x_studio_patas = fields.Integer(string = "Patas", default = 0, store = True)
    x_studio_bajo_encimera = fields.Integer(string = "Bajo Encimera", default = 0, store = True)
    x_studio_desmontar = fields.Integer(string = "Desmontar", default = 0, store = True)
    x_studio_post_cuarzo = fields.Float(string = "Post Cuarzo", default = 0.0, store = True)
    x_studio_tercera_persona = fields.Selection([
        ('si','Si'),
        ('no','No')
        ], string = "Tercera Persona", default='no')

    x_studio_remates_postventa = fields.Integer(string = "Remates PostVenta", default = 0, store = True)
    x_studio_revisin_postventa = fields.Integer(string = "Revisión PostVenta", default = 0, store = True)
    
    x_studio_fecha_reunion = fields.Date(string="Fecha Reunión")
    x_studio_medidor = fields.Many2one('res.partner', string = "Medidor")
    x_studio_montador = fields.Many2one('res.partner', string = "Montador")
    x_studio_obtener_datos = fields.Integer(string='x_studio_obtener_datos', compute='get_obtener_datos')

    x_medidor_purchase_id = fields.Integer(default=0)
    x_montador_purchase_id = fields.Integer(default=0)
    x_purchase_medidor_total = fields.Float(string="Medidor",default=0)
    x_purchase_montador_total = fields.Float(string="Montador",default=0)

    #obtener medidor y montador
    def get_obtener_datos(self):
        self.x_studio_obtener_datos = 0
        if(self.x_studio_oportunidad and (not self.x_studio_montador and not self.x_studio_medidor)):
            meeting_data = self.env['calendar.event'].search([('opportunity_id', '=', self.x_studio_oportunidad.id)], { 'order': 'id desc'})
            for lead in meeting_data:
                for partner in lead.partner_ids:
                    if(partner.user_ids):
                        tipo = partner.user_ids[0].x_studio_subtipo
                        if(tipo == 'Medidor'):
                            self.x_studio_medidor = partner.parent_id.id if partner.parent_id else partner.id
                            self.x_studio_fecha_reunion = meeting_data.start_date
                        elif(tipo == 'Montador'):
                            self.x_studio_montador = partner.parent_id.id if partner.parent_id else partner.id
                            self.x_studio_fecha_reunion = meeting_data.start_date
                        elif(tipo == 'Montador plaza' or tipo == 'Partner plaza'):
                            self.x_studio_montador = partner.parent_id.id if partner.parent_id else partner.id
                            self.x_studio_medidor = partner.parent_id.id if partner.parent_id else partner.id
                            self.x_studio_fecha_reunion = meeting_data.start_date

        self.get_x_studio_instalacion_extra_onchange()
        self.get_x_studio_aplacados_onchange()
        self.get_x_studio_patas_onchange()
        self.get_x_studio_bajo_encimera_onchange()
        self.get_x_studio_desmontar_onchange()
        self.get_x_studio_post_cuarzo_onchange()
        self.get_x_studio_remates_post_venta_onchange()
        self.get_x_studio_revision_post_venta_onchange()

    
    @api.onchange('order_line')
    def x_studio_order_line_onchange(self):
        self.get_x_studio_instalacion_extra_onchange()
        self.get_x_studio_aplacados_onchange()
        self.get_x_studio_patas_onchange()
        self.get_x_studio_bajo_encimera_onchange()
        self.get_x_studio_desmontar_onchange()
        self.get_x_studio_post_cuarzo_onchange()
        self.get_x_studio_remates_post_venta_onchange()
        self.get_x_studio_revision_post_venta_onchange()

    #datetime
    def convert_to_utc(self, local_datetime=None):
        """Convert Localtime to UTC"""
        _localdatetime = datetime.strptime(local_datetime, "%Y-%m-%d  %H:%M:%S")
        timezone_tz = 'utc'
        local = pytz.timezone(timezone_tz)
        local_dt = local.localize(_localdatetime, is_dst=None)
        utc_datetime = local_dt.astimezone(pytz.utc)
        return utc_datetime


    #coronas por medicion
    @api.onchange('x_studio_medicin', 'x_studio_km_medicin')
    def x_studio_corona_onchange(self):
        if(self.x_studio_medidor.x_studio_km_coronas > 0 and self.x_studio_medicin == 'si' and self.x_studio_km_medicin > self.x_studio_medidor.x_studio_km_coronas):
            self.x_studio_coronas_medicin = math.ceil((self.x_studio_km_medicin / self.x_studio_medidor.x_studio_km_coronas) - 1)
        else:
            self.x_studio_coronas_medicin = 0
            
    #coronas por montaje
    @api.onchange('x_studio_montaje', 'x_studio_km_montaje')
    def x_studio_montaje_onchange(self):
        if(self.x_studio_montador.x_studio_km_coronas > 0 and self.x_studio_montaje == 'si' and self.x_studio_km_montaje > self.x_studio_montador.x_studio_km_coronas):
            self.x_studio_coronas_montaje = math.ceil((self.x_studio_km_montaje / self.x_studio_montador.x_studio_km_coronas) - 1)
        else:
            self.x_studio_coronas_montaje = 0

    #instalacion extra
    def get_x_studio_instalacion_extra_onchange(self):
        _total_instalacion_extra = 0
        _index_ini = 0
        _index_end = 0
        self.x_studio_instalacin_extra
        _index_position = self.order_line_section_indexes(self.SECTION_ENCIMERA)
        
        if(len(_index_position) > 0):
            _index_ini = _index_position[0]['ini']
            _index_end = _index_position[0]['end']
       
            for k, _line_data in enumerate(self.order_line):
                if(k > _index_ini and k < _index_end):
                    _total_unidades = _line_data.x_studio_unidades if _line_data.x_studio_unidades > 0 else 1

                    if (_line_data.x_studio_ancho_cm > 0.7):
                        _total_instalacion_extra += _line_data.x_studio_largo_cm_1 * _total_unidades * 2
                    else:
                        _total_instalacion_extra += _line_data.x_studio_largo_cm_1 * _total_unidades
                self.x_studio_instalacin_extra = math.ceil(_total_instalacion_extra) - 3 if math.ceil(_total_instalacion_extra) > 3 else 0

      #aplacados
    def get_x_studio_aplacados_onchange(self):
        _total_aplacados = 0
        _index_ini = 0
        _index_end = 0
        self.x_studio_medir_aplacados = 0
        self.x_studio_colocacin_aplacados = 0
        _index_position = self.order_line_section_indexes(self.SECTION_APLACADO)
        
        if(len(_index_position) > 0):
            _index_ini = _index_position[0]['ini']
            _index_end = _index_position[0]['end']
       
            for k, _line_data in enumerate(self.order_line):
                if(k > _index_ini and k < _index_end):
                    _total_aplacados += _line_data.product_uom_qty
            
            if(_total_aplacados > 0):
                self.x_studio_colocacin_aplacados = _total_aplacados
                self.x_studio_medir_aplacados = 1

    #indices secciones
    def order_line_section_indexes(self, seccion_name):
        _index_section_array = []
        _index_position = []
        #for line in self.order_line:
        for index, line in enumerate(self.order_line):    
            if(line.display_type == 'line_section'):
                _index_section_array.append({'index': index, 'section': line.name.lower().encode('utf-8')})
        #rango de la seccion
        for i, item in enumerate(_index_section_array):    
            if(item['section'] == seccion_name.lower().encode('utf-8')):
                _index_position.append({'ini': item['index'], 'end': _index_section_array[i + 1]['index']})
        
        return _index_position                   
            
    #patas
    def get_x_studio_patas_onchange(self):
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_patas')
        _total_patas = 0
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
                _total_patas += line.product_uom_qty
        self.x_studio_patas = _total_patas
    
    #bajo encimera
    def get_x_studio_bajo_encimera_onchange(self):
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_bajo_encimera')
        _total_bajo_encimera = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
                _total_bajo_encimera += line.product_uom_qty
        self.x_studio_bajo_encimera = _total_bajo_encimera       
                
    #desmontar
    def get_x_studio_desmontar_onchange(self):
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_desmontar')
        _total_desmontar = 0
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
                _total_desmontar += line.product_uom_qty
        self.x_studio_desmontar = _total_desmontar
                
    #post cuarzo
    def get_x_studio_post_cuarzo_onchange(self):    
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_conexiones_post_cuarzo')
        _total_post_cuarzo = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
               _total_post_cuarzo += line.product_uom_qty
        self.x_studio_post_cuarzo = _total_post_cuarzo        
    
    #remates post venta
    def get_x_studio_remates_post_venta_onchange(self):
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_remates_postventa')
        _total_remate_postventa = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
               _total_remate_postventa += line.product_uom_qty
        self.x_studio_remate_postventa = _total_remate_postventa
        
    #revision post venta
    def get_x_studio_revision_post_venta_onchange(self):
        product_name = self.env['ir.config_parameter'].sudo().get_param('x_producto_revision_postventa')
        _total_revision_postventa = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') in line.product_id.name.lower().encode('utf-8')):
               _total_revision_postventa += line.product_uom_qty               
        self.x_studio_revisin_postventa = _total_revision_postventa


    #Save
    def save_cost(self):
        categoria_costes = self.env['ir.config_parameter'].sudo().get_param('x_categoria_costes')
        
        producto_obra = self.env['ir.config_parameter'].sudo().get_param('x_producto_obra')
        producto_tarea_medidor = self.env['ir.config_parameter'].sudo().get_param('x_producto_tareas_medidor')
        producto_km = self.env['ir.config_parameter'].sudo().get_param('x_producto_km')
        producto_coronas = self.env['ir.config_parameter'].sudo().get_param('x_producto_coronas')
        producto_2_medicion = self.env['ir.config_parameter'].sudo().get_param('x_producto_2_medicion')

        producto_tarea_montador = self.env['ir.config_parameter'].sudo().get_param('x_producto_tareas_montador')
        producto_instalacion_extra = self.env['ir.config_parameter'].sudo().get_param('x_producto_instalacion_extra')
        producto_colocacion_aplacados = self.env['ir.config_parameter'].sudo().get_param('x_producto_colocacion_aplacados')
        producto_medir_aplacados = self.env['ir.config_parameter'].sudo().get_param('x_producto_medir_aplacados')
        producto_patas = self.env['ir.config_parameter'].sudo().get_param('x_producto_patas')
        producto_bajo_encimera = self.env['ir.config_parameter'].sudo().get_param('x_producto_bajo_encimera')
        producto_desmontar = self.env['ir.config_parameter'].sudo().get_param('x_producto_desmontar')
        producto_post_cuarzo = self.env['ir.config_parameter'].sudo().get_param('x_producto_conexiones_post_cuarzo')
        producto_3_persona = self.env['ir.config_parameter'].sudo().get_param('x_producto_3_persona')
        producto_remate_post_venta = self.env['ir.config_parameter'].sudo().get_param('x_producto_remates_postventa')
        producto_revision_post_venta = self.env['ir.config_parameter'].sudo().get_param('x_producto_revision_postventa')

        # purchase order
        is_purchase_medidor = True if ((self.x_studio_obra == 'si' and self.x_studio_coste_medicin > 0) or (self.x_studio_medicin == "si")) else False
        is_purchase_montador = True if ((self.x_studio_obra == 'si' and self.x_studio_coste_montaje > 0) or (self.x_studio_montaje == "si")) else False
        purchase_medidor = self.crud_purchase_order(self.x_studio_medidor, 'medidor', is_purchase_medidor)
        purchase_montador = self.crud_purchase_order(self.x_studio_montador, 'montador', is_purchase_montador)

        # purchase order line
        is_obra = True if self.x_studio_obra == 'si' else False
        purchase_medidor = self.crud_purchase_order_line(purchase_medidor, categoria_costes, producto_obra, self.x_studio_coste_medicin, is_obra)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_obra, self.x_studio_coste_montaje, is_obra)

        is_medicion = True if self.x_studio_medicin == "si" else False
        is_2_medicion = True if is_medicion and self.x_studio_2_medicin == "si" else False
        purchase_medidor = self.crud_purchase_order_line(purchase_medidor, categoria_costes, producto_tarea_medidor, 1, is_medicion)
        purchase_medidor = self.crud_purchase_order_line(purchase_medidor, categoria_costes, producto_km, self.x_studio_km_medicin, is_medicion)
        purchase_medidor = self.crud_purchase_order_line(purchase_medidor, categoria_costes, producto_coronas, self.x_studio_coronas_medicin, is_medicion)
        purchase_medidor = self.crud_purchase_order_line(purchase_medidor, categoria_costes, producto_2_medicion, 1, is_2_medicion)

        is_montador = True if self.x_studio_montaje == "si" or self.x_studio_montaje == "incidencia" else False
        is_3_pax = True if is_montador and self.x_studio_tercera_persona == "si" else False
        is_incidencia = True if self.x_studio_montaje == "si" and self.x_studio_montaje == "incidencia" else False
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_tarea_montador, 1, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_km, self.x_studio_km_montaje, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_coronas, self.x_studio_coronas_montaje, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_instalacion_extra, self.x_studio_instalacin_extra, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_colocacion_aplacados, self.x_studio_colocacin_aplacados, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_medir_aplacados, self.x_studio_medir_aplacados, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_patas, self.x_studio_patas, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_bajo_encimera, self.x_studio_bajo_encimera, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_desmontar, self.x_studio_desmontar, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_post_cuarzo, self.x_studio_post_cuarzo, is_montador)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_3_persona, 1, is_3_pax)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_remate_post_venta, self.x_studio_remates_postventa, is_incidencia)
        purchase_montador = self.crud_purchase_order_line(purchase_montador, categoria_costes, producto_revision_post_venta, self.x_studio_revisin_postventa, is_incidencia)

        if(purchase_medidor):
            self.x_purchase_medidor_total = purchase_medidor.amount_untaxed
        if(purchase_montador):
            self.x_purchase_montador_total = purchase_montador.amount_untaxed
    
        #Actualizar costos del presupuesto
        if(self.x_studio_obra == 'si'):
            self.x_studio_medicin = 'no'
            self.x_studio_montaje = 'no'
        if(self.x_studio_medicin == 'no'):
            self.x_studio_km_medicin = 0
            self.x_studio_coronas_medicin = 0
            self.x_studio_2_medicin = 'no'
        if(self.x_studio_montaje == 'no'):
            self.x_studio_km_montaje = 0
            self.x_studio_coronas_montaje = 0
            self.x_studio_instalacin_extra = 0
            self.x_studio_colocacin_aplacados = 0.0
            self.x_studio_medir_aplacados = 0
            self.x_studio_patas = 0
            self.x_studio_bajo_encimera = 0
            self.x_studio_desmontar = 0
            self.x_studio_post_cuarzo = 0.0
            self.x_studio_tercera_persona = 'no'
            self.x_studio_remates_postventa = 0
            self.x_studio_revisin_postventa = 0

        self.write({
            'x_medidor_purchase_id': purchase_medidor.id if purchase_medidor else False,
            'x_montador_purchase_id': purchase_montador.id if purchase_montador else False,
            'x_studio_obra': self.x_studio_obra,
            'x_studio_coste_medicin': self.x_studio_coste_medicin,       
            'x_studio_coste_montaje': self.x_studio_coste_montaje,
            'x_studio_medicin': self. x_studio_medicin,
            'x_studio_km_medicin': self.x_studio_km_medicin,
            'x_studio_coronas_medicin': self.x_studio_coronas_medicin,
            'x_studio_2_medicin': self.x_studio_2_medicin,
            'x_studio_montaje': self.x_studio_montaje,
            'x_studio_km_montaje': self.x_studio_km_montaje,
            'x_studio_coronas_montaje': self.x_studio_coronas_montaje,
            'x_studio_instalacin_extra': self.x_studio_instalacin_extra,
            'x_studio_colocacin_aplacados': self.x_studio_colocacin_aplacados,
            'x_studio_medir_aplacados': self.x_studio_medir_aplacados,
            'x_studio_patas': self.x_studio_patas,
            'x_studio_bajo_encimera': self.x_studio_bajo_encimera,
            'x_studio_desmontar': self.x_studio_desmontar,
            'x_studio_post_cuarzo': self.x_studio_post_cuarzo,
            'x_studio_tercera_persona': self.x_studio_tercera_persona,
            'x_studio_remates_postventa': self.x_studio_remates_postventa,
            'x_studio_revisin_postventa': self.x_studio_revisin_postventa,
            'x_studio_medidor': self.x_studio_medidor,
            'x_studio_montador': self.x_studio_montador
        })
        return self

    def crud_purchase_order(self, partner_id, type, is_add_or_edit):
        purchase = False
        if(is_add_or_edit):
            if(partner_id):
                if(type == 'medidor'):
                    purchase = self.env['purchase.order'].search([('origin','=',self.name),('id','=',self.x_medidor_purchase_id)])
                elif(type == 'montador'):
                    purchase = self.env['purchase.order'].search([('origin','=',self.name),('id','=',self.x_montador_purchase_id)])
                if(not purchase):
                    purchase = self.env['purchase.order'].create({
                        'partner_id': partner_id.id,
                        'origin': self.name,
                        'date_order': self.x_studio_fecha_reunion if self.x_studio_fecha_reunion else datetime.now(),
                        'state':'draft'
                    })
        else:
            purchase_delete = self.env['purchase.order'].search([('origin','=',self.name),('id','=',partner_id.id)])
            if purchase_delete:
                purchase_delete.write({
                    'state': 'cancel'
                })
                purchase_delete.unlink()

        return purchase

    def crud_purchase_order_line(self, purchase, categoria_padre_name, producto_name, quantity, is_add_or_edit):
        if(purchase):
            price_list = self.env['product.supplierinfo'].search([
                ('product_tmpl_id.categ_id.parent_id.name','=', categoria_padre_name),\
                ('product_tmpl_id.name','=', producto_name),\
                ('name','=',purchase.partner_id.id)], limit=1)
                    
            if(price_list):
                order_line = self.env['purchase.order.line'].search([('order_id','=',purchase.id),('product_id','=',price_list.product_tmpl_id.product_variant_id.id)])
                if(is_add_or_edit and quantity > 0):
                    if(order_line):
                        order_line.write({
                            'product_qty': quantity,
                            'price_unit': price_list.price
                        })
                    else:
                        order_line = self.env['purchase.order.line'].create({
                            'order_id': purchase.id,
                            'product_id': price_list.product_tmpl_id.product_variant_id.id,
                            'name': price_list.product_tmpl_id.product_variant_id.display_name,
                            'product_qty': quantity,
                            'product_uom': price_list.product_tmpl_id.uom_id.id,
                            'price_unit': price_list.price,
                            'date_planned': fields.Datetime.to_string(datetime.today()),
                        })
                        order_line.onchange_product_id()
                        
                else:
                    if(order_line):
                        order_line.unlink()

        return purchase

    @api.depends('order_line.margin')
    def _product_margin(self):
        super(cost_calculation_custom_0, self)._product_margin()
        calculate_margin = self.margin - self.x_purchase_medidor_total - self.x_purchase_montador_total
        self.margin = calculate_margin if calculate_margin > 0 else 0