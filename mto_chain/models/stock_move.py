
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    raw_mto_parent = fields.Many2one(
        string=u'MTO Parent',
        comodel_name='sale.order.line',
        compute='_compute_mto_parent',
    )
    
    @api.depends('raw_material_production_id')
    def _compute_mto_parent(self):
        for move in self:
            origin_move = move
            while move:
                production = move.raw_material_production_id
                if not production:
                    move = move.move_dest_ids[0] if move.move_dest_ids else False
                else:
                    if production.node_id:
                        raw_mto_parent = production.node_id._get_parent()
                        if raw_mto_parent.res_model == 'sale.order.line':
                            origin_move.raw_mto_parent = raw_mto_parent.record_ref
                    break