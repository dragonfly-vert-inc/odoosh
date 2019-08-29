# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SPDModel(models.Model):
    _inherit = 'stock.picking'

    sp_delivery_date = fields.Datetime('Delivery Date')