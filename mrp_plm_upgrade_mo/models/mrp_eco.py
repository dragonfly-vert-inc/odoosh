
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

class ReportBomStructure(models.AbstractModel):
    _name = 'report.mrp.report_eco_changes'
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        all_ecos = self.env['mrp.eco'].search([('id','child_of',self.env.context.get('active_id'))])
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(line.product_id.standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.user.company_id.currency_id.round(sub_total)
            child_bom_id = all_ecos.filtered(lambda eco: eco.product_tmpl_id.id == line.product_id.product_tmpl_id.id).new_bom_id
            components.append({
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and self._get_bom_reference(line.child_bom_id) or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': self.env.user.company_id.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
        return components, total

    @api.model
    def get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        lines = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
        return self.env.ref('mrp_plm_upgrade_mo.eco_change_report_line').render({'data': lines})

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        if not bom_id:
            if self._context.get('active_id', False):
                eco = self.env['mrp.eco'].browse(self._context['active_id'])
                bom_id = eco.new_bom_id.id
        lines = super(ReportBomStructure, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        if self._context.get('active_id', False):
            eco = self._context['active_id']
            active_eco = self.env['mrp.eco'].search([('id','child_of',eco),'|',('bom_id','=',bom_id),('new_bom_id','=',bom_id)])
            lines['eco_changes'] = active_eco.bom_change_ids
        return lines

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        res = self._get_report_data(bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant)
        res['lines']['report_type'] = 'html'
        res['lines']['report_structure'] = 'all'
        res['lines']['has_attachments'] = res['lines']['attachments'] or any(component['attachments'] for component in res['lines']['components'])
        res['lines'] = self.env.ref('mrp_plm_upgrade_mo.eco_change_report').render({'data': res['lines']})
        return res

class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    _parent_store = True

    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(comodel_name='mrp.eco', ondelete='set null')
    child_ids = fields.One2many(comodel_name='mrp.eco',inverse_name='parent_id',)
    

    @api.multi
    def action_new_revision(self):
        super(MrpEco, self).action_new_revision()
        Bom = self.env['mrp.bom']
        Eco = self.env['mrp.eco']
        for eco in self:
            if eco.type in ('bom', 'both') and not eco.parent_id:
                child_boms = eco.bom_id.bom_line_ids.mapped('child_bom_id')
                all_boms = self.env['mrp.bom']
                while(child_boms):
                    all_boms += child_boms
                    child_boms = child_boms.mapped('bom_line_ids').mapped('child_bom_id')
                all_boms = all_boms.mapped(lambda self: self)
                eco.write({
                    'child_ids': [(0, 0, {
                            'name': '%s (%s)' %(child_bom.display_name, eco.name),
                            'type_id': eco.type_id.id,
                            'type': 'bom',
                            'product_tmpl_id': child_bom.product_tmpl_id.id,
                            'bom_id': child_bom.id,
                            'stage_id': eco.stage_id.id}) for child_bom in all_boms]
                    })
                eco.child_ids.action_new_revision()

    @api.multi
    def open_all_components(self):
        action = self.env.ref('mrp.mrp_bom_form_action').read()[0]
        child_boms = self.env['mrp.eco'].search([('id', 'child_of',self.id)]).mapped('new_bom_id')
        return dict(action, domain=[('id', 'in', child_boms.ids)], context={"search_default_inactive": True})

    @api.multi
    def open_all_components_bom(self):
        action = self.env.ref('mrp_plm_upgrade_mo.bom_line_action').read()[0]
        child_boms = self.env['mrp.eco'].search([('id', 'child_of',self.id)]).mapped('new_bom_id')
        return dict(action, domain=[('bom_id', 'in', child_boms.ids)], context={"search_default_bom_group": True})

    @api.multi
    def button_upgrade_mo(self):
        if self.bom_id and self.new_bom_id:
            pending_orders = self.env['mrp.production'].search([('bom_id','=',self.bom_id.id),('state','in',('confirmed','planned'))])
            update_orders = pending_orders.filtered(lambda p: p.check_mto_progress())
            for production in update_orders:
                prev_child_mo = production.node_id.get_childs().filtered(lambda r: r.res_model == 'mrp.production').mapped('record_ref') - production
                finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                raw_moves._do_unreserve()
                raw_moves._action_cancel()
                raw_moves.sudo().unlink()
                picking_ids = production.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                picking_ids.action_cancel()
                if production.workorder_ids:
                    production.workorder_ids.unlink()
                    production.state = 'confirmed'
                production.bom_id = self.new_bom_id
                production._generate_moves()
                finish_moves._do_unreserve()
                finish_moves._action_cancel()
                message = "Bills of Material Updated from: <a href=# data-oe-model=%s data-oe-id=%d>%s</a>" % (self._name, self.id, self.name)
                cancel_message = "MO Canceled from: <a href=# data-oe-model=%s data-oe-id=%d>%s</a>" % (self._name, self.id, self.name)
                for mo in prev_child_mo:
                    mo.action_cancel()
                    mo.message_post(body=cancel_message)
                production.message_post(body=message)
                production.eco_updated = True
                
            # if update_orders:
            #     return dict(self.env.ref('mrp.mrp_production_action').read()[0], domain=[('id','in',update_orders.ids)])
    

    @api.multi
    def write(self, vals):
        res = super(MrpEco, self).write(vals)
        for e in self:
            if vals.get('stage_id') and not e.parent_id:
                for child_eco in (self.search([('id','child_of',e.id)]) - e):
                    child_eco.write({
                        'stage_id': vals.get('stage_id')
                    })
        return res

    @api.multi
    def approve(self):
        super(MrpEco, self).approve()
        for eco in self:
            if not eco.parent_id:
                for child_eco in (self.search([('id','child_of',eco.id)]) - eco):
                    child_eco.approve()

    @api.multi
    def reject(self):
        super(MrpEco, self).reject()
        for eco in self:
            if not eco.parent_id:
                for child_eco in (self.search([('id','child_of',eco.id)]) - eco):
                    child_eco.reject()
    
    @api.multi
    def action_apply(self):
        super(MrpEco, self).action_apply()
        for eco in self:
            if not eco.parent_id:
                for child_eco in (self.search([('id','child_of',eco.id)]) - eco):
                    child_eco.action_apply()
        return self.env.ref('mrp_plm_upgrade_mo.apply_update').read()[0]

    @api.multi
    def get_all_eco(self):
        action = self.env.ref('mrp_plm.mrp_eco_action_main').read()[0]
        return dict(action, domain=[('id','child_of', self.id)], context={})



class ApplyUpdateWizard(models.TransientModel):
    _name = 'apply.update.wizard'
    _description = 'Apply update Wizard'

    @api.multi
    def action_apply(self):
        return self.env['mrp.eco'].browse(self._context.get('active_id')).button_upgrade_mo()