
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

    res_model = fields.Char()
    res_id = fields.Integer()
    record_ref = fields.Reference(selection=[('purchase.order', 'Purchase Order'), ('mrp.production', 'Manufacturing Order'), ('sale.order.line'), ('Sale Order Line')],
                                  compute='_get_ref',
                                  store=True)

    priority_id = fields.Many2one(comodel_name='mto.priority', ondelete='restrict')

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

    priority_id = fields.Many2one(string='MTO Priority',
        comodel_name='mto.priority', ondelete='set null', related="node_id.priority_id", readonly=False, store=True)
    color = fields.Char(related='priority_id.color')

    @api.model
    def create(self, values):
        node_id = self.node_id.create({}).id
        values.update({'node_id': node_id})
        result = super(MTOChainMixin, self).create(values)
        result.node_id._set_ref(result)
        return result

