# -*- coding: utf-8 -*-

# from odoo import models, fields, api, _
# from datetime import timedelta
# from odoo.tools import float_round
# import logging
# _logger = logging.getLogger(__name__)
#
# class SPDModel(models.Model):
#     _inherit = 'stock.move'
#
#     date_expected = fields.Datetime(related='sale_line_id.date_expected');
#     date_expected_sol = fields.Datetime(related='sale_line_id.date_expected');
#     sale_delay = fields.Float(related='product_id.product_tmpl_id.sale_delay');