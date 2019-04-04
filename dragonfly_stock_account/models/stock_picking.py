# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = ['stock.picking']

    switch_off = fields.Boolean(string='Switch off',  help="checked will activate the more advance automated inventory valuation, if unchecked standard behaviour is used while inventory valuation")


class StockLocation(models.Model):
    _inherit = 'stock.location'

    custom_stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Valuation Account',
        company_dependent=True,
        domain=[('deprecated', '=', False)],
        help="When real-time inventory valuation is enabled on a product, this account will hold the current value of the products.",)
