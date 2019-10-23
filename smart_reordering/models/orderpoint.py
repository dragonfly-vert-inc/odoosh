
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class StockReorder(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    
    lead_days = fields.Integer(store="True", related="product_id.reorder_lead_days")    
    