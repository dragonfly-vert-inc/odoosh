# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    manager_approval_amount = fields.Monetary(
        string='Manager Amount',
        default=1,
        help="Minimum amount for which a manager approval is required")
    vp_approval_amount = fields.Monetary(
        string='VP Amount',
        default=500,
        help="Minimum amount for which a vice president approval is required")
    vp_finance_approval_amount = fields.Monetary(
        string='VP Finance Amount',
        default=2000,
        help="Minimum amount for which a vice president finance approval is required")
    ceo_approval_amount = fields.Monetary(
        string='COO Amount',
        default=10000,
        help="Minimum amount for which a coo approval is required")
    cfo_approval_amount = fields.Monetary(
        string='CFO Amount',
        default=25000,
        help="Minimum amount for which a cfo approval is required")
