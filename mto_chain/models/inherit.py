
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    _inherit = ['sale.order.line', 'mto.chain.mixin']

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLine, self).default_get(fields)
        res['priority_id'] = self.env['mto.priority'].search([],order='sequence DESC', limit=1).id
        return res

class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    _inherit = ['purchase.order', 'mto.chain.mixin']


class MrpProduction(models.Model):
    _name = 'mrp.production'

    _inherit = ['mrp.production', 'mto.chain.mixin']

