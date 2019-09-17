
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
            if move.raw_material_production_id.node_id:
                raw_mto_parent = move.raw_material_production_id.node_id._get_parent()
                if raw_mto_parent.res_model == 'sale.order.line':
                    move.raw_mto_parent = raw_mto_parent.record_ref