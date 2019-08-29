# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SOLModel(models.Model):
    _inherit = 'sale.order.line'

    sol_delivery_date = fields.Datetime('Delivery Date')

    sol_priority = fields.Selection([
        ('1', 'Low'), ('2', 'Medium'), ('3', 'High'),
    ], string='Priority')

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id', 'sol_delivery_date', 'sol_priority']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    def _get_protected_fields(self):
        return [
            'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty',
            'tax_id', 'analytic_tag_ids', 'sol_delivery_date', 'sol_priority'
        ]

    # @api.multi
    # def update_fields(self):
    #     sales_line_ids = self.env['sale.order.line'].search([('product_id', '=', self.id)])
    #     Example_ids = []
    #     for line in Example_line_ids:
    #         if line.order_id:
    #             Example_ids.append(line.order_id.id)
    #
    #     view_id = self.env.ref('product_Example.view_tree_tree').id
    #     form_view_id = self.env.ref('product_Example.view_Example_order_view').id
    #     context = self._context.copy()
    #     return {
    #         'name': 'form_name',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'Example.order',
    #         'view_id': view_id,
    #         'views': [(view_id, 'tree'), (form_view_id, 'form')],
    #         'type': 'ir.actions.act_window',
    #         'domain': [('id', 'in', Example_ids)],
    #         'target': 'current',
    #         'context': context,
    #     }