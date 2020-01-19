
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    view_adjust_bill = fields.Boolean(compute='compute_view_adjust_bill')

    @api.multi
    @api.depends('order_line')
    def compute_view_adjust_bill(self):
        for PO in self:
            if PO.state == 'purchase' and any(PO.order_line.mapped( lambda line: float_compare(line.qty_received, line.qty_invoiced, precision_digits=2) == -1 )):
                PO.view_adjust_bill = True
            else:
                PO.view_adjust_bill = False

    @api.multi
    def bill_refund(self):
        self.ensure_one()
        adjustable_lines = self.env['purchase.order.line']
        for POL in self.order_line:
            if float_compare(POL.qty_received , POL.qty_invoiced, precision_digits=2) == -1:
                adjustable_lines += POL
        if adjustable_lines:
            invoices = adjustable_lines.mapped('invoice_lines').mapped('invoice_id').filtered(lambda invoice: invoice.type == 'in_invoice')
            if all(invoices.mapped(lambda invoice: invoice.state != 'draft')):
                new_invoices = self.env['account.invoice']
                for invoice in invoices:
                    invoice_purchase_lines = invoice.invoice_line_ids.mapped('purchase_line_id')
                    matched_lines = adjustable_lines & invoice_purchase_lines
                    if matched_lines:
                        quant_dict = {}
                        for line in matched_lines:
                            quant_dict[line.id] = line.qty_invoiced - line.qty_received

                        values = self.env['account.invoice']._prepare_refund(invoice, date_invoice=fields.Date.today(), date=False,
                                                description='Return', journal_id=invoice.journal_id.id)
                        preapared_lines = []
                        
                        for value in values['invoice_line_ids']:
                            if value[2]['purchase_line_id'] in quant_dict:
                                value[2]['quantity'] = quant_dict[value[2]['purchase_line_id']]
                                del(quant_dict[value[2]['purchase_line_id']])
                            else:
                                value[2]['quantity'] = 0
                            preapared_lines.append(value)
                        values.update({
                            'invoice_line_ids': preapared_lines
                        })
                        refund_invoice = invoice.create(values)
                        refund_invoice.compute_taxes()
                        invoice_type = {'out_invoice': ('customer invoices credit note'),
                            'in_invoice': ('vendor bill credit note')}
                        message = _("This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>") % (invoice_type[invoice.type], invoice.id, invoice.number)
                        refund_invoice.message_post(body=message)
                        adjustable_lines = adjustable_lines - matched_lines
                        new_invoices += refund_invoice
            else:
                raise UserError('Invoices are in draft state.')