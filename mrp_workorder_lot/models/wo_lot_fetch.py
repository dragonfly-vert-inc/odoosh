# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class MRPLotFetch(models.Model):
    _inherit = "mrp.workorder"
    reserved_lot_ids = fields.Many2many('stock.production.lot', compute='_compute_reserved_lots')

    @api.depends('production_id')
    def _compute_reserved_lots(self):
        for wo in self:
            wo.update({'reserved_lot_ids': [(6, 0, wo.production_id.move_raw_ids.mapped('active_move_line_ids').mapped('lot_id').ids)]})


    def _next(self, state='pass'):
        """ This function:
        - first: fullfill related move line with right lot and validated quantity.
        - second: Generate new quality check for remaining quantity and link them to the original check.
        - third: Pass to the next check or return a failure message.
        """
        self.ensure_one()
        if self.qty_producing <= 0 or self.qty_producing > self.qty_remaining:
            raise UserError(_('Please ensure the quantity to produce is nonnegative and does not exceed the remaining quantity.'))
        elif self.test_type == 'register_consumed_materials':
            # Form validation
            if self.component_tracking != 'none' and not self.lot_id:
                raise UserError('You must select a serial number from the dropdown. If the serial number on the picking order is not present or is different from the actual one, please add or change it on the picking order first.')
            if self.component_tracking == 'none' and self.qty_done <= 0:
                raise UserError(_('Please enter a positive quantity.'))

            self._update_active_move_line()

            self._create_subsequent_checks()

        if self.test_type == 'picture' and not self.picture:
            raise UserError(_('Please upload a picture.'))

        self.current_quality_check_id.write({
            'quality_state': state,
            'user_id': self.env.user.id,
            'control_date': datetime.now()})
        if self.skip_completed_checks:
            self._change_quality_check(increment=1, children=1, checks=self.skipped_check_ids)
        else:
            self._change_quality_check(increment=1, children=1)