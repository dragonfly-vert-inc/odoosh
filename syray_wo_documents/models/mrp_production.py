from odoo import models, api, fields, _


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    reserved_lot_ids = fields.One2many(compute="_compute_reserved_lots")

    @api.depends('move_raw_ids')
    def _compute_reserved_lots(self):
        for production in self:
            production.reserved_lot_ids = production.move_raw_ids.mapped('active_move_line_ids').mapped('lot_id')