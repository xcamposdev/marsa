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
    x_studio_segunda_medicin = fields.Integer(string = "Segunda Medición", default = 0)
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
    x_studio_medidor = fields.Many2one('res.partner', string = "Medidor", readonly=True)
    x_studio_montador = fields.Many2one('res.partner', string = "Montador", readonly=True)
    x_studio_obtener_datos = fields.Integer( string = 'x_studio_obtener_datos', compute = 'get_obtener_datos')

    #obtener medidor
    def get_obtener_datos(self):
        if(self.x_studio_oportunidad and (not self.x_studio_montador and not self.x_studio_medidor)):
            meeting_data = self.env['calendar.event'].search([('opportunity_id', '=', self.x_studio_oportunidad.id)], { 'order': 'id desc'})
            montador = False
            medidor = False
            for lead in meeting_data:
                for partner in lead.partner_ids:
                    if(partner.user_ids):
                        tipo = partner.user_ids[0].x_studio_subtipo
                        if(tipo == 'Medidor'):
                            medidor = partner.id
                        elif(tipo == 'Montador'):
                            montador = partner.id
                        elif(tipo == 'Montador plaza' or tipo == 'Partner plaza'):
                            montador = partner.id
                            medidor = partner.id
            if montador:
                self.x_studio_montador = montador
            if medidor:
                self.x_studio_medidor = medidor
        else:
            self.x_studio_oportunidad = False

        self.get_x_studio_instalacion_extra_onchange()
        self.get_x_studio_aplacados_onchange()
        self.get_x_studio_patas_onchange()
        self.get_x_studio_bajo_encimera_onchange()
        self.get_x_studio_desmontar_onchange()
        self.get_x_studio_post_cuarzo_onchange()
        self.get_x_studio_remates_post_venta_onchange()
        self.get_x_studio_revision_post_venta_onchange()

        self.x_studio_obtener_datos = 0

    #Medicion por obra
    @api.onchange('x_studio_obra')
    def x_studio_obra_onchange(self):
        if(self.x_studio_obra == 'si'):
            self.x_studio_medicin = 'no'
            self.x_studio_km_medicin = 0
            self.x_studio_coronas_medicin = 0
            self.x_studio_2_medicin = 'no'
            self.x_studio_segunda_medicin = 0
            self.x_studio_montaje = 'no'
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

        else:
            self.x_studio_coste_medicin = 0
            self.x_studio_coste_montaje = 0        
            
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
    @api.onchange('order_line')
    def x_studio_instalacion_extra_onchange(self):
        self.get_x_studio_instalacion_extra_onchange()
        self.get_x_studio_aplacados_onchange()
        self.get_x_studio_patas_onchange()
        self.get_x_studio_bajo_encimera_onchange()
        self.get_x_studio_desmontar_onchange()
        self.get_x_studio_post_cuarzo_onchange()
        self.get_x_studio_remates_post_venta_onchange()
        self.get_x_studio_revision_post_venta_onchange()
    
    def get_x_studio_instalacion_extra_onchange(self):
        _total_instalacion_extra = 0
        _total_metros_lineales = 0
        _total_unidades = 1
        _ancho_pieza = 0 
        _metros_lineales = 0
        _index_ini = 0
        _index_end = 0
        _index_position = self.order_line_section_indexes(self.SECTION_ENCIMERA)
        
        if(len(_index_position) > 0):
            _index_ini = _index_position[0]['ini']
            _index_end = _index_position[0]['end']
       
        for k, _line_data in enumerate(self.order_line):
            if(k > _index_ini and k < _index_end):
                _metros_lineales = _line_data.x_studio_largo_cm_1
                _ancho_pieza = _line_data.x_studio_ancho_cm
                _total_unidades = _line_data.x_studio_unidades if _line_data.x_studio_unidades > 0 else 1

                if(_metros_lineales > 3):
                    _total_instalacion_extra += math.ceil((_metros_lineales * _total_unidades) - 3)
                elif(_metros_lineales <= 3):
                    if (_ancho_pieza > 0.7):
                        _total_instalacion_extra += math.ceil((_metros_lineales * _total_unidades * 2) - 3)
                    elif (_ancho_pieza <= 0.7):
                        _total_instalacion_extra += math.ceil((_metros_lineales * _total_unidades) - 3)
                
            self.x_studio_instalacin_extra = _total_instalacion_extra 

    #segunda medicion
    @api.onchange('x_studio_2_medicin')
    def x_studio_segunda_medicion_onchange(self):
        if(self.x_studio_2_medicin == 'si'):
            self.x_studio_segunda_medicin = 1
        else:
            self.x_studio_segunda_medicin = 0
    
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
        product_name = 'PATAS'
        _total_patas = 0
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
                _total_patas += line.product_uom_qty
        self.x_studio_patas = _total_patas
    
    #bajo encimera
    def get_x_studio_bajo_encimera_onchange(self):
        product_name = 'BAJO ENCIMERA'
        _total_bajo_encimera = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
                _total_bajo_encimera += line.product_uom_qty
        self.x_studio_bajo_encimera = _total_bajo_encimera       
                
    #desmontar
    def get_x_studio_desmontar_onchange(self):
        product_name = 'DESMONTAR'
        _total_desmontar = 0
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
                _total_desmontar += line.product_uom_qty
        self.x_studio_desmontar = _total_desmontar
                
    #post cuarzo
    def get_x_studio_post_cuarzo_onchange(self):    
        product_name = 'CONEXIONES'
        _total_post_cuarzo = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
               _total_post_cuarzo += line.product_uom_qty
        self.x_studio_post_cuarzo = _total_post_cuarzo        
    
    #remates post venta
    def get_x_studio_remates_post_venta_onchange(self):
        product_name = 'REMATES POSTVENTA'
        _total_remate_postventa = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
               _total_remate_postventa += line.product_uom_qty
        self.x_studio_remate_postventa = _total_remate_postventa
        
    #revision post venta
    def get_x_studio_revision_post_venta_onchange(self):
        product_name = 'REVISIÓN POSTVENTA'
        _total_revision_postventa = 0 
        for line in self.order_line:
            if(line.display_type != 'line_section' and product_name.lower().encode('utf-8') == line.product_id.name.lower().encode('utf-8')):
               _total_revision_postventa += line.product_uom_qty               
        self.x_studio_revisin_postventa = _total_revision_postventa

    def save_cost(self):
        #Crear orden de compra para medidor
        if(self.x_studio_medidor):
            self.env['purchase.order'].create({
                    'partner_id': self.x_studio_medidor.id,
                    # 'order_line': [(0, 0, {
                    #     'product_id': ?,
                    #     'name': ?,
                    #     'date_planned': ?,
                    #     'price_unit': ? }), 
                    #     ] 
            })
        
        #Crear orden de compra para montador
        if(self.x_studio_montador):
            self.env['purchase.order'].create({
                    'partner_id': self.x_studio_montador.id,
                    # 'order_line': [(0, 0, {
                    #     'product_id': ?,
                    #     'name': ?,
                    #     'date_planned': ?,
                    #     'price_unit': ? }), 
                    #     ] 
            })

        #Actualizar costos del presupuesto
        self.write({
            'x_studio_obra': self.x_studio_obra,
            'x_studio_coste_medicin': self.x_studio_coste_medicin,       
            'x_studio_coste_montaje': self.x_studio_coste_montaje,
            'x_studio_medicin': self. x_studio_medicin,
            'x_studio_km_medicin': self.x_studio_km_medicin,
            'x_studio_coronas_medicin': self.x_studio_coronas_medicin,
            'x_studio_2_medicin': self.x_studio_2_medicin,
            'x_studio_segunda_medicin': self.x_studio_segunda_medicin,
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