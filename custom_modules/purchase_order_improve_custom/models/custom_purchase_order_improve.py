# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class PurchaseOrderImproveCustom(models.Model):

    _inherit = 'purchase.order'
    
    x_origin_opportunity = fields.Char(string="Documento Origen Op.")
    x_origin = fields.Char(string='Documento origen', compute='get_origin_value_compute', inverse="get_origin_value_inverse")

    def get_origin_value_compute(self):
        for record in self:
            if record.x_origin_opportunity:
                record.x_origin = record.x_origin_opportunity
            else:
                record.x_origin = record.origin

    def get_origin_value_inverse(self):
        for record in self:
            if record.x_origin:
                if record.x_origin_opportunity:
                    record.x_origin_opportunity = record.x_origin
                else:
                    record.origin = record.x_origin
