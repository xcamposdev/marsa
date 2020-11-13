# -*- coding: utf-8 -*-

import logging
import copy
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

