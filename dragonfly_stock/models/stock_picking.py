# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = ['stock.picking']

    sub_location_id = fields.Many2one(related="sale_id.sub_location_id", string="Location", store=True)
    is_auto_fill = fields.Boolean(related="sale_id.is_auto_fill", string="Location Auto-fill")
    is_pick = fields.Boolean(related="picking_type_id.is_pick", string="Is Pick")


class PickingType(models.Model):
    _inherit = ['stock.picking.type']
    is_pick = fields.Boolean(string="Is Pick Type", help="Use to set if the type should be considered Pick.")


class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    @api.model_create_multi
    def create(self, vals_list):
        mls = super(StockMoveLine, self).create(vals_list)
        # Check if the boolean was set. Use write to change the "To" Location if it is a Pick
        for ml in mls.filtered(lambda xmll: xmll.picking_id.is_auto_fill and xmll.picking_id.is_pick):
            ml.location_dest_id = ml.picking_id.sub_location_id
        return mls
