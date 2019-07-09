# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models,fields
from odoo.exceptions import UserError
from odoo import exceptions
import logging
_logger = logging.getLogger(__name__)


class AttachmentWizard(models.TransientModel):
    _name = 'syray.product.attachment.wizard'
