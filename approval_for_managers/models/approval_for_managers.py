
from odoo.exceptions import Warning
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('approve', 'Waiting For Approval'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('reject', 'Reject'),
        ('cancelled', 'Cancelled'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    
    def button_confirm(self):
        self.write({
            'state': 'approve'
        })

    def button_approved(self):
        for order in self:
            if order.state not in ['draft', 'sent','approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
        # rec = super(PurchaseOrderInh, self).button_confirm()

    def button_reject(self):
        self.write({
            'state': 'reject'
        })

    def button_cancel(self):
        self.write({
            'state': 'cancelled'
        })

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'


    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('approve', 'Waiting For Approval'),
        ('sale', 'Sales Order'),
        ('reject', 'Reject'),
        ('done', 'Locked'),
        ('cancelled', 'Cancelled'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')


    def action_confirm(self):
        self.write({
            'state': 'approve'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancelled'
        })

    def action_drafts(self):
        self.write({
            'state': 'draft'
        })

    def button_approve(self):
        rec = super(SaleOrderInh, self).action_confirm()

    def button_reject(self):
        self.write({
            'state': 'reject'
        })

class MRPProductionInh(models.Model):
    _inherit = 'mrp.production'


    is_check_availability = fields.Boolean(string='Check Availability', default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('approve', 'Waiting For Approval'),
        ('reject', 'Reject'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * Planned: The WO are planned.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")

    def action_button_plan(self):
        self.write({
            'state': 'approve'
        })


    def action_assign(self):
        res = super(MRPProductionInh, self).action_assign()
        if self.move_raw_ids:
            for rec in self.move_raw_ids:
                if rec.product_uom_qty == rec.reserved_availability:
                    if self.is_check_availability == False:
                        self.is_check_availability = True

        return res


    def action_set_to_draft(self):
        self.write({
            'state': 'draft'
        })


    def button_approve(self):
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'approve')
        for order in orders_to_plan:
            order.move_raw_ids.filtered(lambda m: m.state == 'draft')._action_confirm()
            quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
            boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
            order._generate_workorders(boms)
            order._plan_workorders()
        return True


    def button_reject(self):
        self.write({
            'state': 'reject'
        })


class AccountMoveInh(models.Model):
    _inherit = 'account.move'


    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approve', 'Waiting For Approval'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('reject', 'Reject')
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    def action_post(self):
        self.write({
            'state': 'approve'
        })

    def button_approve(self):
        rec = super(AccountMoveInh, self).action_post()

    def button_reject(self):
        self.write({
            'state': 'reject'
        })


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Waiting For Approval'),
                              ('posted', 'Validated'),
                              ('sent', 'Sent'),
                              ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('reject', 'Reject')
                              ], readonly=True, default='draft', copy=False, string="Status")

    def action_post(self):
        self.write({
            'state': 'approve'
        })

    def button_approve(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:

            if rec.state != 'approve':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids')\
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                    .reconcile()

        return True


    def button_reject(self):
        self.write({
            'state': 'reject'
        })



class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('approve', 'Waiting For Approval'),
        ('done', 'Done'),
        ('reject', 'Reject'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state', copy=False,
        index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def button_validate(self):
        if self.picking_type_id.code == 'internal':
            self.write({
                'state': 'approve'
            })
        else:
            rec = super(StockPickingInh, self).button_validate()
            return rec

    # def action_validate(self):
    #     self.write({
    #         'state': 'approve'
    #     })

    def button_approved(self):
            rec = super(StockPickingInh, self).button_validate()
            return rec

    def button_reject(self):
        self.write({
            'state': 'reject'
        })
