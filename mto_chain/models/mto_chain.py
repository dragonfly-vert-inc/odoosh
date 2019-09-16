
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MTOChain(models.Model):
    _name = 'mto.chain'
    _description = u'MTO Chain'

    _rec_name = 'record_ref'
    _order = 'res_model ASC, res_id ASC'

    @api.model
    def _get_models(self):
        mixin = self.env.ref('mto_chain.model_mto_chain_mixin')
        return [(model.model, model.name) for model in mixin.inherited_model_ids]

    res_model = fields.Char()
    res_id = fields.Integer()
    record_ref = fields.Reference(selection=[('purchase.order', 'Purchase Order'),('mrp.production','Manufacturing Order'),('sale.order.line'),('Sale Order Line')],
                                  compute='_get_ref',
                                  store=True)

    parent_ids = fields.Many2many(
        string=u'Parents',
        comodel_name='mto.chain',
        relation='mto_parent_child_rel',
        column1='parent_id',
        column2='child_id',
    )

    child_ids = fields.Many2many(
        string=u'Childs',
        comodel_name='mto.chain',
        relation='mto_parent_child_rel',
        column2='parent_id',
        column1='child_id',
    )

    @api.depends('res_model', 'res_id')
    def _get_ref(self):
        for participant in self:
            if participant.res_model:
                participant.record_ref = '%s,%s' % (
                    participant.res_model, participant.res_id or 0)

    @api.multi
    def _set_ref(self, record):
        self.ensure_one()
        record.ensure_one()
        self.write({'res_model': record._name, 'res_id': record.id})
        return self

    @api.model
    def get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        if active_id and active_model:
            rcontext['node_id'] = self.env[active_model].browse(
                active_id).node_id
            result['html'] = self.env.ref(
                'mto_chain.mto_cascade_view').render(rcontext)
        return result

    @api.model
    def _get_parent(self):
        self.ensure_one()
        node = self
        while (node.parent_ids):
            node = node.parent_ids
            if len(node) > 1:
                node = False
        return node

class MTOChainMixin(models.AbstractModel):
    _name = 'mto.chain.mixin'

    node_id = fields.Many2one(
        comodel_name='mto.chain',
        ondelete='set null')

    @api.model
    def create(self, values):
        result = super(MTOChainMixin, self).create(values)
        result.node_id = self.node_id.create({})._set_ref(result)
        return result


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    _inherit = ['sale.order.line', 'mto.chain.mixin']

    @api.multi
    def view_mto_chain(self):
        action = dict(self.env.ref('mto_chain.action_mto_chain').read()[
                      0], domain=[('id', 'child_of', self.node_id.id)])
        return action


class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    _inherit = ['purchase.order', 'mto.chain.mixin']


class MrpProduction(models.Model):
    _name = 'mrp.production'

    _inherit = ['mrp.production', 'mto.chain.mixin']


class StockMove(models.Model):
    _inherit = 'stock.move'

    need_to_procure = fields.Boolean(default=True)

    purchase_line_ids = fields.One2many(
        string=u'Linked Purchase Line',
        comodel_name='purchase.raw.link',
        inverse_name='raw_consumption_id',
    )

    free_quantity = fields.Float(compute='_get_free_quantity')

    @api.depends('product_uom_qty', 'reserved_availability', 'purchase_line_ids')
    def _get_free_quantity(self):
        for sm in self:
            sm.free_quantity = sm.product_uom_qty - sm.reserved_availability - \
                sum(sm.purchase_line_ids.mapped('quantity'))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    raw_consumption_ids = fields.One2many(
        string=u'Linked Consumption Line',
        comodel_name='purchase.raw.link',
        inverse_name='purchase_line_id',
    )

    free_quantity = fields.Float(compute='_get_free_quantity')

    @api.depends('product_qty', 'raw_consumption_ids')
    def _get_free_quantity(self):
        for pl in self:
            pl.free_quantity = pl.product_qty - \
                sum(pl.raw_consumption_ids.mapped('quantity'))

    @api.multi
    @api.depends('product_id', 'order_id')
    def name_get(self):
        return [(pl.id, "%s / %s" % (pl.product_id.name, pl.order_id.name)) for pl in self]


class PurchaseRawLink(models.Model):
    _name = 'purchase.raw.link'
    _description = u'Procurement Raw Material Consumption Linking'

    _order = 'id ASC'

    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        ondelete='set null',
        required=True
    )

    raw_consumption_id = fields.Many2one(
        comodel_name='stock.move',
        ondelete='set null',
        required=True
    )

    quantity = fields.Float(
        required=True,
        readonly=True
    )

    @api.onchange('raw_consumption_id', 'purchase_line_id')
    def _onchange_raw_purchase(self):
        self.quantity = min(self.raw_consumption_id.free_quantity,
                            self.purchase_line_id.free_quantity)

    @api.multi
    def link_manual_procurement(self):
        child_node = self.purchase_line_id.order_id.node_id
        parent_node = self.raw_consumption_id.raw_material_production_id.node_id
        child_node.write({'parent_ids': [(4, parent_node.id, False)]})
