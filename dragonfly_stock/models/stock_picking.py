# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = ['stock.picking']

    sub_location_id = fields.Many2one(related="sale_id.sub_location_id", string="Location", store=True)
    is_auto_fill = fields.Boolean(related="sale_id.is_auto_fill", string="Location Auto-fill")
    is_pick = fields.Boolean(compute="_compute_is_pick", string="Is Pick", store=True)

    @api.multi
    @api.depends('picking_type_id', 'picking_type_id.is_pick')
    def _compute_is_pick(self):
        for pick in self:
            pick.is_pick = pick.picking_type_id.is_pick


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


# Overwrite the return picking create method to differentiate between a return pick and a standard pick
class ReturnPicking(models.TransientModel):
    _inherit = ['stock.return.picking']

    def _create_returns(self):
        new_pick, pick_type = super(ReturnPicking, self)._create_returns()

        for pick in self.env['stock.picking'].browse(new_pick):
            for line in pick.move_line_ids_without_package:
                line.write({'location_dest_id': pick.location_dest_id.id})
            pick.is_pick = False
        return new_pick, pick_type
