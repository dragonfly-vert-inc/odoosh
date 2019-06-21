# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError

PO_APPROVAL_STATE = [
    'manager_approval',
    'vp_approval',
    'vp_finance_approval',
    'ceo_approval'
]


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Purchase Order Type"

    name = fields.Char(required=True)
    manager = fields.Many2one('hr.employee', string='Manager')
    controller = fields.Many2many('hr.employee', string='Controllers')
    vice_president = fields.Many2one('hr.employee', string='Vice President')
    vice_president_finance = fields.Many2one('hr.employee', string='Vice President Finance')
    ceo = fields.Many2one('hr.employee', string='CEO')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    po_type_id = fields.Many2one('purchase.order.type', string='PO Type', track_visibility='onchange')
    state = fields.Selection(selection=[
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('manager_approval', 'Manager Approval'),
        ('vp_approval', 'VP Approval'),
        ('vp_finance_approval', 'VP Finance Approval'),
        ('ceo_approval', 'CEO Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])
    show_approval_btn = fields.Boolean(compute='_compute_show_approval_btn')

    @api.multi
    def _compute_show_approval_btn(self):
        for po in self.filtered(lambda p: p.state in ['manager_approval', 'vp_approval', 'ceo_approval', 'vp_finance_approval']):
            po.show_approval_btn = po._is_valid_user_for_approval()

    @api.multi
    def button_reject(self):
        self.ensure_one()
        # send rejection message to followers + anyone in the PO approval chain
        partners_to_notify = self.message_partner_ids
        if self.state == 'ceo_approval':
            partners_to_notify |= (self.po_type_id.vice_president.user_id.partner_id + self.po_type_id.vice_president_finance.user_id.partner_id + self.po_type_id.manager.user_id.partner_id)
        elif self.state == 'vp_finance_approval':
            partners_to_notify |= self.po_type_id.manager.user_id.partner_id
            approval_amount = self._get_approval_amount()
            if self.amount_total >= approval_amount['vp_amount']:
                partners_to_notify |= self.po_type_id.vice_president.user_id.partner_id
        elif self.state == 'vp_approval':
            partners_to_notify |= self.po_type_id.manager.user_id.partner_id
        template = self.env.ref('dragonfly_purchase.mail_template_po_reject')
        template.send_mail(self.id, force_send=True, email_values={'recipient_ids': [(4, p.id) for p in partners_to_notify]})

        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'manager_approval', 'vp_approval', 'vp_finance_approval', 'ceo_approval']:
                continue
            order._add_supplier_to_product()
            # =========== Comment Current flow Start============
            # Deal with double validation process
            # if order.company_id.po_double_validation == 'one_step'\
            #         or (order.company_id.po_double_validation == 'two_step'\
            #             and order.amount_total < self.env.user.company_id.currency_id._convert(
            #                 order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
            #         or order.user_has_groups('purchase.group_purchase_manager'):
            #     order.button_approve()
            # else:
            #     order.write({'state': 'to approve'})
            # =========== Comment Current flow Start============
            # Custom Code Start
            order._approve_order()
            # Custom Code End
        return True

    def _need_approval(self, approval_amount):
        if (not self.po_type_id or
                self.company_id.po_double_validation != 'two_step' or
                self.amount_total < approval_amount['vp_finance_amount'] or
                self.user_has_groups('account.group_account_manager')):
            return False
        return True

    def _get_user_in_cc(self, approval_amount):
        users_to_add_as_follower = self.env['res.users']
        if self.amount_total < approval_amount['manager_amount']:
            users_to_add_as_follower |= self.po_type_id.manager.user_id
        users_to_add_as_follower |= self.po_type_id.controller.mapped('user_id')
        return users_to_add_as_follower

    def _get_approval_state(self, state=False, approval_amount=None):
        amount = self.amount_total
        state = state or self.state
        if amount < approval_amount['manager_amount'] and state in ('draft', 'sent'):
            result = 'vp_finance_approval'
        elif amount >= approval_amount['manager_amount'] and state in ('draft', 'sent'):
            result = 'manager_approval'
        elif amount >= approval_amount['vp_amount'] and state == 'manager_approval':
            result = 'vp_approval'
        elif amount >= approval_amount['vp_finance_amount'] and state in ('manager_approval', 'vp_approval'):
            result = 'vp_finance_approval'
        elif amount >= approval_amount['ceo_amount'] and state == 'vp_finance_approval':
            result = 'ceo_approval'
        else:
            result = False

        users_by_state = self._get_user_by_approval_state()
        if result and not users_by_state.get(result):
            result = self._get_approval_state(result, approval_amount)
        state_by_user = self._get_state_by_user()
        if result and state_by_user.get(self.env.uid) and PO_APPROVAL_STATE.index(state_by_user.get(self.env.uid)) >= PO_APPROVAL_STATE.index(result):
            result = self._get_approval_state(state_by_user.get(self.env.uid), approval_amount)
        return result

    def _is_valid_user_for_approval(self):
        uid = self.env.uid
        users_by_state = self._get_user_by_approval_state()
        state_by_user = self._get_state_by_user()
        if (self.state in ['draft', 'sent'] or
                self.user_has_groups('account.group_account_manager') or
                uid == users_by_state[self.state].id or
                (state_by_user.get(self.env.uid) and PO_APPROVAL_STATE.index(state_by_user.get(self.env.uid)) > PO_APPROVAL_STATE.index(self.state))):
            return True
        return False

    def _notify_user_for_next_approval(self, state):
        users_by_state = self._get_user_by_approval_state()
        self._send_message(user=users_by_state[state])

    def _get_approval_amount(self):
        """
            Return the minimum amount required for approval of each entity
        """
        currency = self.env.user.company_id.currency_id
        today = fields.Date.today()
        return {
            'manager_amount': currency._convert(self.company_id.manager_approval_amount, self.currency_id, self.company_id, self.date_order or today),
            'vp_amount': currency._convert(self.company_id.vp_approval_amount, self.currency_id, self.company_id, self.date_order or today),
            'vp_finance_amount': currency._convert(self.company_id.vp_finance_approval_amount, self.currency_id, self.company_id, self.date_order or today),
            'ceo_amount': currency._convert(self.company_id.ceo_approval_amount, self.currency_id, self.company_id, self.date_order or today),
        }

    def _get_user_by_approval_state(self):
        return {
            'manager_approval': self.po_type_id.manager.user_id,
            'vp_approval': self.po_type_id.vice_president.user_id,
            'vp_finance_approval': self.po_type_id.vice_president_finance.user_id,
            'ceo_approval': self.po_type_id.ceo.user_id,
        }

    def _get_state_by_user(self):
        # TODO: swap key, value with _get_user_by_approval_state
        return {
            self.po_type_id.manager.user_id.id: 'manager_approval',
            self.po_type_id.vice_president.user_id.id: 'vp_approval',
            self.po_type_id.vice_president_finance.user_id.id: 'vp_finance_approval',
            self.po_type_id.ceo.user_id.id: 'ceo_approval',
        }

    @api.multi
    def _approve_order(self):
        self.ensure_one()
        approval_amount = self._get_approval_amount()
        if self._need_approval(approval_amount):
            if not self._is_valid_user_for_approval():
                raise UserError(_('You are not allowed to confirm the order.'))
            if self.state in ('draft', 'sent'):
                self._add_follower_with_message(users=self._get_user_in_cc(approval_amount))
            state = self._get_approval_state(approval_amount=approval_amount)
            if not state:
                if self.user_has_groups('account.group_account_manager') or self.po_type_id and self.env.uid in self._get_state_by_user().keys():
                    return self.button_approve()
                raise UserError(_('You are not allowed to confirm the order.'))
            self._notify_user_for_next_approval(state)
            self.write({'state': state})
        else:
            # keep PO in cc
            self._add_follower_with_message(users=self._get_user_in_cc(approval_amount))
            self.button_approve()
        return True

    def _send_message(self, user=None):
        if not user:
            return
        msg_body = _("<a href=# data-oe-model=res.partner data-oe-id=%d>@%s</a> Your Approval is required for Purchase Order") % (user.partner_id.id, user.partner_id.name)
        self.message_post(body=msg_body, partner_ids=user.partner_id.ids)
        # Hack to forcefully unsubsribe since this 'mail_post_autofollow' context is forcefully passed in purchase message post
        self.message_unsubscribe(partner_ids=user.partner_id.ids)

    def _add_follower_with_message(self, users=None):
        if not users:
            return
        message = _('<div><p>Hello,</p><p>%s invited you to follow %s document: %s.</p></div>') % (self.env.user.partner_id.name, self._description, self.display_name)
        mail_invite = self.env['mail.wizard.invite']
        for user in users:
            mail_invite |= self.env['mail.wizard.invite'].create({
                'res_model': self._name,
                'res_id': self.id,
                'partner_ids': [(4, user.partner_id.id)],
                'message': message,
                'send_mail': True
            })
        mail_invite.add_followers()
