# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, exceptions

_logger = logging.getLogger(__name__)

class calculator_custom_0(models.Model):
    
    _inherit = 'sale.order'

    @api.onchange('x_studio_oportunidad')
    def _onchange_x_studio_oportunidad(self):
#         a = self.env['model.model'].search_read([('create_date', '=', fields.datetime.now())])
# json.dumps(header), 

        _logger.info("TEST %s", json.dumps(self))
#         values = self._onchange_partner_id_values(self.partner_id.id if self.partner_id else False)
#         self.update(values)
        