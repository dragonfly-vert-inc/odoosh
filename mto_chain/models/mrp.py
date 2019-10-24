
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    priority_id = fields.Many2one(
        comodel_name='mto.priority', ondelete='set null', related="production_id.priority_id", store=True)
    color = fields.Char(related='priority_id.color')
    released = fields.Boolean(related="production_id.released")

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    released = fields.Boolean(default=False, readonly=True)

    @api.multi
    def button_release(self):
        self.write({
            'released': True
        })
            
    @api.multi
    def button_unrelease(self):
        self.write({
            'released': False
        })