
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account.mrp_cost_structure'


    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(MrpCostStructure, self)._get_report_values(docids, data)
        productions = self.env['mrp.production']\
            .browse(docids)\
            .filtered(lambda p: p.state != 'cancel')
        if all([production.state == 'done' for production in productions]):
            res['workorders'] = productions.mapped('workorder_ids')
            res['currency_id'] = self.env.user.company_id.currency_id
        return res
