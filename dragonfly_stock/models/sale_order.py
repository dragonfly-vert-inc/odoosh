# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = ['sale.order']

    sub_location_id = fields.Many2one('stock.location', "Location",default=False, store=True)
    is_auto_fill = fields.Boolean(string="Location Auto-fill", store=True)


    @api.onchange('is_auto_fill')
    def _onchange_auto_fill(self):
        for pick in self.picking_ids.filtered(lambda pk: pk.is_pick and pick.state not in  ('done', 'cancel')):
            for line in pick.move_line_ids_without_package:
                if self.is_auto_fill and self.sub_location_id:
                    line.location_dest_id = self.sub_location_id
                else:
                    line.location_dest_id = pick.location_dest_id

    @api.onchange('sub_location_id')
    def _onchange_sub_location(self):
        if self.is_auto_fill and self.sub_location_id:
            for pick in self.picking_ids.filtered(lambda pk: pk.is_pick and pick.state not in  ('done', 'cancel')):
                for line in pick.move_line_ids_without_package:
                    line.location_dest_id = self.sub_location_id