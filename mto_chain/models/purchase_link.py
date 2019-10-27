
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PoMoLink(models.TransientModel):
    _name = 'procurement.linking'
    _description = u'Procurement Raw Material Consumption Linking'


    line_ids = fields.One2many(comodel_name='procurement.linking.line',inverse_name='linking_id',)
    linked = fields.Boolean(default=False)
    

    @api.multi
    def link_manual_procurement(self):
        for linking in self:
            for line in linking.line_ids:
                line.production_id.node_id.write({
                    'child_ids': [(4, line.purchase_id.node_id.id, False)]
                })
            linking.linked = True

class PoMoLinkingLine(models.TransientModel):
    _name = 'procurement.linking.line'
    _description = u'Procurement Raw Material Consumption Linking Line'

    
    purchase_id = fields.Many2one(
        string=u'Purchase',
        comodel_name='purchase.order',
        ondelete='set null',
    )
    production_id = fields.Many2one(
        string=u'Production',
        comodel_name='mrp.production',
        ondelete='set null',
    )
    
    linking_id = fields.Many2one(
        comodel_name='procurement.linking',
        ondelete='set null',
    )
    
    