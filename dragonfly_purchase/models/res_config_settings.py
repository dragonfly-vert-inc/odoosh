# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manager_approval_amount = fields.Monetary(
        related='company_id.manager_approval_amount',
        currency_field='company_currency_id',
        readonly=False)
    vp_approval_amount = fields.Monetary(
        related='company_id.vp_approval_amount',
        currency_field='company_currency_id',
        readonly=False)
    vp_finance_approval_amount = fields.Monetary(
        related='company_id.vp_finance_approval_amount',
        currency_field='company_currency_id',
        readonly=False)
    ceo_approval_amount = fields.Monetary(
        related='company_id.ceo_approval_amount',
        currency_field='company_currency_id',
        readonly=False)
