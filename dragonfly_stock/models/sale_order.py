# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = ['sale.order']

    sub_location_id = fields.Many2one('stock.location', "Location",default=False, store=True)
    is_auto_fill = fields.Boolean(string="Location Auto-fill", store=True)

    # @api.onchange('is_auto_fill')
    # def _auto_fill_to(self):
    #     print("HERE")
    #     if self.is_auto_fill:
    #         for pick in self.picking_ids:
    #             for move in pick.move_line_ids_without_package:
    #                 print("pre " + str(move.location_dest_id))
    #                 print(self.sub_location_id)
    #                 move.location_dest_id = self.sub_location_id
    #                 print("post " + str(move.location_dest_id))

    @api.onchange('is_auto_fill')
    def _onchange_auto_fill(self):
        print("HELLO I AM CHANGED")
        if self.is_auto_fill:
            if self.picking_ids:
                print(self.picking_ids)
                for pick in self.picking_ids:
                    #TODO: check with best way of identifying the picking type: Pick
                    if pick.is_pick:
                        for line in pick.move_line_ids_without_package:
                            # call write to set the "To" location to the current one
                            line.write({'location_dest_id': self.sub_location_id.id})
            else:
                print("no pickings")
        else:
            print("I AM FALSE")
            if self.picking_ids:
                for pick in self.picking_ids:
                    if pick.is_pick:
                        for line in pick.move_line_ids_without_package:
                            # set the "To" Location to the original standard location
                            line.write({'location_dest_id': pick.location_dest_id.id})

    @api.onchange('sub_location_id')
    def _onchange_sub_location(self):
        print("HELLO LOCATION IS CHANGED")
        if self.is_auto_fill:
            if self.picking_ids:
                print(self.picking_ids)
                for pick in self.picking_ids:
                    #TODO: check with best way of identifying the picking type: Pick
                    if pick.is_pick:
                        for line in pick.move_line_ids_without_package:
                            # call write to set the "To" location to the current one
                            line.write({'location_dest_id': self.sub_location_id.id})
            else:
                print("no pickings")
        else:
            print("I AM FALSE")
