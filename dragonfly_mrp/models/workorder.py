# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    public_url = fields.Char(related="current_quality_check_id.public_url")
