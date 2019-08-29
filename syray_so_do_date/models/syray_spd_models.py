# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SPDModel(models.Model):
    _inherit = 'stock.move'


    date_expected = fields.Datetime(related='sale_line_id.sol_delivery_date');