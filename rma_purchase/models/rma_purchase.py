
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class RMATemplate(models.Model):
    _inherit = 'rma.template'

    
    from_purchase = fields.Boolean(default=False)
    from_inv = fields.Boolean(default=False, string="From Adjustment")
    
    