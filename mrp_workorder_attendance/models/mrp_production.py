# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def force_action_cancel(self):
        for wo in self.mapped('workorder_ids').filtered(lambda wo: wo.state == 'progress'):
            if not wo.check_ids.filtered(lambda check: check.quality_state != 'none'):
                wo.check_ids.unlink()
                wo.action_cancel()
                timeline = self.env['mrp.workcenter.productivity'].search([('workorder_id','=',wo.id)])
                if timeline:
                    timeline.unlink()
            else:
                raise UserError("Work Orders steps already performed, can not cancel.")
        return  self.action_cancel()

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        super(MRPProduction, self)._cal_price(consumed_moves)
        worker_cost = 0
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            for work_order in self.workorder_ids:
                duration = sum(work_order.worker_times.mapped('worked_hours'))
                worker_cost += duration * work_order.workcenter_id.cost_hour_employee
            if finished_move.product_id.cost_method in ('fifo', 'average'):
                qty_done = finished_move.product_uom._compute_quantity(finished_move.quantity_done, finished_move.product_id.uom_id)
                finished_move.price_unit += (worker_cost/ qty_done)
                finished_move.value += worker_cost
        return True