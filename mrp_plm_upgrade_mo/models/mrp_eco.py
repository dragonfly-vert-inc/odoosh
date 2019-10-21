
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    @api.multi
    def button_upgrade_mo(self):
        if self.bom_id and self.new_bom_id:
            pending_orders = self.env['mrp.production'].search([('bom_id','=',self.bom_id.id),('state','in',('confirmed','planned'))])
            for production in pending_orders:
                finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                (finish_moves | raw_moves)._do_unreserve()
                (finish_moves | raw_moves)._action_cancel()
                (finish_moves | raw_moves).unlink()
                picking_ids = production.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                picking_ids.action_cancel()
                picking_ids.unlink()
                if production.workorder_ids:
                    production.workorder_ids.unlink()
                    production.state = 'confirmed'
                production.bom_id = self.new_bom_id
                production._generate_moves()
            if pending_orders:
                return dict(self.env.ref('mrp.mrp_production_action').read()[0], domain=[('id','in',pending_orders.ids)])