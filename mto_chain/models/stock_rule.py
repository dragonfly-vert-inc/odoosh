
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        res = super(StockRule, self)._run_manufacture(product_id, product_qty, product_uom, location_id, name, origin, values)
        origin_move = values.get('move_dest_ids') and values['move_dest_ids'][0]
        production_id = origin_move.created_production_id
        if production_id:
            while origin_move:
                if origin_move.sale_line_id:
                    origin_record = origin_move.sale_line_id
                elif origin_move.raw_material_production_id: 
                    origin_record = origin_move.raw_material_production_id
                    origin_move.need_to_procure = False
                else:
                    origin_record = False
                if origin_record:
                    production_id.node_id.write({
                            'parent_ids': [(6,False,origin_record.node_id.ids)],
                        })
                    child_node = origin_record.node_id
                    while(child_node):
                        child_node.priority_id = origin_record.node_id.priority_id.id
                        child_node = child_node.child_ids
                    break
                else:
                    origin_move = origin_move.move_dest_ids[0] if origin_move.move_dest_ids else origin_move.move_dest_ids
        return res
