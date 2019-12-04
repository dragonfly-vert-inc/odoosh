
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RMA(models.Model):
    _inherit = 'rma.rma'

    from_purchase = fields.Boolean(related="template_id.from_purchase")
    from_inv = fields.Boolean(related="template_id.from_inv")
    purchase_id = fields.Many2one(
        string='Purchase', comodel_name='purchase.order', ondelete='set null')
    inventory_id = fields.Many2one(
        string='Inventory Adjustment', comodel_name='stock.inventory', ondelete='set null')

    invoice_id = fields.Many2one(
        string='Invoice', comodel_name='account.invoice', ondelete='set null')

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.stock_picking_id = self.env['stock.picking'].search([('purchase_id', '=', self.purchase_id.id),('picking_type_code','=','incoming')], limit=1)

    @api.multi
    def open_invoice(self):
        action = self.env.ref('account.action_invoice_in_refund').read()[0]
        return dict(action, views=[(False, 'form')], res_id=self.invoice_id.id)

    @api.multi
    def create_credit_note(self):
        lines = []
        for line in self.lines:
            taxes = line.product_id.supplier_taxes_id
            account = self.env['account.invoice.line'].get_invoice_line_account(
                type, line.product_id, self.partner_id.property_account_position_id, self.env.user.company_id)
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.done_qty,
                'uom_id': line.product_uom_id.id,
                'name': line.product_id.name,
                'origin': self.name,
                'price_unit': line.product_id.standard_price,
                'invoice_line_tax_ids': [(6, 0, taxes.ids)],
                'account_id': account.id,
            }))
        self.invoice_id = self.env['account.invoice'].with_context({'default_type': 'in_refund', 'type': 'in_refund', 'journal_type': 'purchase'}).create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'name': self.name,
            'invoice_line_ids': lines
        })
        action = self.env.ref('account.action_invoice_in_refund').read()[0]
        return dict(action, views=[(False, 'form')], res_id=self.invoice_id.id)

    def _create_out_picking(self):
        res = super(RMA, self)._create_out_picking()
        res.rma_id = self
        return res


class RMAPickingMakeLines(models.TransientModel):
    _inherit = 'rma.picking.make.lines'

    def _create_lines(self):
        make_lines_obj = self.env['rma.picking.make.lines.line']
        if not self.rma_id.template_usage and self.rma_id.inventory_id:
            for l in self.rma_id.inventory_id.move_ids:
                self.line_ids |= make_lines_obj.create(self._line_values(l))
        else:
            super(RMAPickingMakeLines, self)._create_lines()


class RMALine(models.Model):
    _inherit = 'rma.line'

    done_qty = fields.Float(string='Done', compute='_compute_done')
    def _compute_done(self):
        for line in self:
            lines = self.env['stock.picking'].search([('rma_id','=',line.rma_id.id)]).mapped('move_lines').filtered(lambda l: l.state == 'done' and l.product_id == line.product_id)
            line.done_qty = sum(lines.mapped('quantity_done'))

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    rma_id = fields.Many2one(comodel_name='rma.rma',ondelete='set null',)