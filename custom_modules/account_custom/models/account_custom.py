# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby

from odoo import api, fields, models, exceptions, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class AccountMoveCustom0(models.Model):

    _inherit = 'account.move'

    x_importe_comision = fields.Float(compute='get_importe_comision')

    def get_importe_comision(self):
        for rec in self:
            rec.x_importe_comision = rec.amount_total * rec.x_importe_comision/100

    @api.onchange('partner_id')
    def custom_onchange_partner_id(self):
        self.x_studio_referenciador = self.partner_id.x_studio_referenciador
        super(AccountMoveCustom0, self)._onchange_partner_id()

    @api.onchange('x_studio_referenciador')
    def custom_onchange_x_studio_referenciador(self):
        self.x_studio_comisin = self.x_studio_referenciador.x_studio_comisin
