# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    employee_ids = fields.Many2many(
        string=u'Employees',
        comodel_name='hr.employee',
        relation='working_employee_workorder_rel',
        column1='emp_id',
        column2='wo_id')

    employee_popup_id = fields.Many2one(comodel_name='workorder.add.employee', ondelete='set null')

    worker_times = fields.One2many(comodel_name='hr.attendance', inverse_name='wo_id', readonly=True)

    @api.multi
    def open_employee_popup(self):
        if not self.employee_popup_id:
            self.employee_popup_id = self.env['workorder.add.employee'].create({'wo_id': self.id})
        return {
            'name': _('Add/Edit Workers'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'workorder.add.employee',
            'res_id': self.employee_popup_id.id,
            'target': 'new'
        }

    def write(self, vals):
        if 'employee_ids' in vals and len(self) == 1:
            workers_before_write = self.employee_ids
            res = super(MRPWorkorder, self).write(vals)
            workers_after_write = self.employee_ids
            added_workers = workers_after_write - workers_before_write
            deleted_workers = workers_before_write - workers_after_write
            if added_workers:
                added_workers.workorder_to_checkin(self.id)
            if deleted_workers:
                deleted_workers.workorder_to_checkout(self.id)
            return res
        else:
            return super(MRPWorkorder, self).write(vals)

    def button_start(self):
        breakpoint()
        user_id = self.env.user
        employee_id = self.env['hr.employee'].search([('user_id', '=', user_id.id)], limit=1)
        if not employee_id:
            employee_id = self.env['hr.employee'].sudo().create({'name': user_id.name, 'user_id': user_id.id})
        self.write({'employee_ids': [(4, employee_id.id, False)]})
        return super(MRPWorkorder, self).button_start()

    def do_finish(self):
        threshold = self.env.user.company_id.manufacturing_worked_hour_threshold
        for wo in self:
            wo.employee_ids.workorder_to_checkout(self.id)
            wo.worker_times.filtered(lambda att: att.worked_hours <= threshold).unlink()
        return super(MRPWorkorder, self).do_finish()