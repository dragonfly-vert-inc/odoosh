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
