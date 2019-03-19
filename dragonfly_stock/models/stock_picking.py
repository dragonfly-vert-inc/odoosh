# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = ['stock.picking']

    sub_location_id = fields.Many2one(related="sale_id.sub_location_id", string="Location", store=True)
    is_auto_fill = fields.Boolean(related="sale_id.is_auto_fill", string="Location Auto-fill")
    is_pick = fields.Boolean(related="picking_type_id.is_pick", string="Is Pick")

    # @api.onchange('is_auto_fill')
    # def _onchange_auto_fill(self):
    #     print("HELLO I AM CHANGED")

    # @api.onchange('is_auto_fill')
    # def _auto_fill_to(self):
    #     print("HERE")
    #     if self.is_auto_fill:
    #         for move in self.move_line_ids_without_package:
    #             print(move.produc_id.name)
    #             move.location_dest_id = self.sub_location_id

    # @api.multi
    # @api.depends('move_line_ids')
    # def _compute_sale_order(self):
    #     for record in self:
    #         for move in move_line_ids:
    #

class PickingType(models.Model):
    _inherit = ['stock.picking.type']
    is_pick = fields.Boolean(string="Is Pick Type", help="Use to set if the type should be considered Pick.")

class StockMoveLine(models.Model):
    _inherit = ['stock.move.line']

    @api.model_create_multi
    def create(self, vals_list):
        print("in overwrite create")
        mls = super(StockMoveLine, self).create(vals_list)

        # Check if the boolean was set. Use write to change the "To" Location
        for ml in mls:
            if ml.picking_id.is_auto_fill:
                ml.write({'location_dest_id': ml.picking_id.sub_location_id.id})
        return mls

    def write(self, vals):
        print("in overwrite write")
        res = super(StockMoveLine, self).write(vals)
        return res

    #new_dest_id = fields.Many2one('stock.location', string='To')

    # @api.multi
    # @api.depends('picking_id')
    # def _compute_location(self):
    #     for line in self:
    #         if line.picking_id.sub_location_id:
    #             print("pre stock" + str(self.location_dest_id))
    #             self.location_dest_id = line.picking_id.sub_location_id
    #             print("post stock" + str(self.location_dest_id))
    #             self.new_dest_id = line.picking_id.sub_location_id
