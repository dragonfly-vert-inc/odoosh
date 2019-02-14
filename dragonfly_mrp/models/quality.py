# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    survey_template_id = fields.Many2one('survey.survey', string="Quality Check Survey Template")
    public_url = fields.Char("public_url")

    @api.onchange('user_id', 'survey_template_id')
    def onchange_set_token(self):
        public_url = self.survey_template_id and self.survey_template_id.public_url or ''
        if self.user_id and self.survey_template_id:
            user_input = self.survey_template_id.user_input_ids.filtered(lambda r: r.partner_id == self.user_id.partner_id)
            public_url += user_input and '/' + user_input[0].token or ''
        self.public_url = public_url


class QualityCheck(models.Model):
    _inherit = "quality.check"

    public_url = fields.Char(related="point_id.public_url")
