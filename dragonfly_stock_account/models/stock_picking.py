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


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _is_internal(self):
        """
            Used to check wheather intermediate accounting entry required or not
        """
        for move_line in self.move_line_ids.filtered(lambda ml: not ml.owner_id):
            if move_line.location_id._should_be_valued() and\
                move_line.location_dest_id._should_be_valued() and\
                move_line.picking_id.switch_off and\
                    (move_line.location_dest_id.custom_stock_valuation_account_id or move_line.location_id.custom_stock_valuation_account_id):
                return True
        return False

    def _get_inventory_value(self):
        if self.product_id.cost_method in ['standard', 'average']:
            quantity = self.env.context.get('forced_quantity', self.product_qty)
            correction_value = quantity * self.product_id.standard_price
            return correction_value
        return self.value

    def _account_entry_move(self):
        """Inherited in order to generate the intermediate accoutning entries for internal transfer"""
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.product_id.type != 'product':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if self._is_in():
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_from and location_from.usage == 'customer':  # goods returned from customer
                self.with_context(force_company=company_to.id)._create_account_move_line(acc_dest, acc_valuation, journal_id)
            else:
                self.with_context(force_company=company_to.id)._create_account_move_line(acc_src, acc_valuation, journal_id)

        # Create Journal Entry for products leaving the company
        if self._is_out():
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_to and location_to.usage == 'supplier':  # goods returned to supplier
                self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_src, journal_id)
            else:
                # CSUTOM CHANGES START
                if self.picking_id.switch_off and location_from.custom_stock_valuation_account_id:
                    acc_valuation = location_from.custom_stock_valuation_account_id.id
                # CUSTOM CHANGES END
                self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_dest, journal_id)

        if self.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if self._is_dropshipped():
                self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_src, acc_dest, journal_id)
            elif self._is_dropshipped_returned():
                self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_dest, acc_src, journal_id)

        if self.company_id.anglo_saxon_accounting:
            #eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            self._get_related_invoices()._anglo_saxon_reconcile_valuation(product=self.product_id)
        # CSUTOM CHANGES START
        if self._is_internal():
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if self.picking_code == 'internal' and location_from.custom_stock_valuation_account_id and location_to.custom_stock_valuation_account_id and location_from.custom_stock_valuation_account_id.id != location_to.custom_stock_valuation_account_id.id:
                self.with_context(force_company=self.location_id.company_id.id, force_valuation_amount=self._get_inventory_value())._create_account_move_line(
                    location_from.custom_stock_valuation_account_id.id, location_to.custom_stock_valuation_account_id.id, journal_id)
            elif self.picking_code == 'internal' and location_from.custom_stock_valuation_account_id and not location_to.custom_stock_valuation_account_id:
                self.with_context(force_company=self.location_id.company_id.id, force_valuation_amount=self._get_inventory_value())._create_account_move_line(location_from.custom_stock_valuation_account_id.id, acc_valuation, journal_id)
            else:
                acc_dest = self.location_dest_id.custom_stock_valuation_account_id.id
                self.with_context(force_company=self.location_id.company_id.id, force_valuation_amount=self._get_inventory_value())._create_account_move_line(acc_valuation, acc_dest, journal_id)
        # CUSTOM CHANGES END

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        for move in res.filtered(lambda m: m.product_id.valuation == 'real_time' and m._is_internal()):
            move._account_entry_move()
        return res
