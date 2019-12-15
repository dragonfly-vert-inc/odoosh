
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    
    eco_updated = fields.Boolean(string='Eco updated', default=False, readonly=True)
    