# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree

from odoo.exceptions import UserError


class MaterialRequisitioninh(models.Model):
    _inherit = 'material.purchase.requisition'

    check_purchases = fields.Boolean("Check Purchase", compute='_compute_state_purchase')
    # check_internal = fields.Boolean("Check Internal", compute='_compute_state_internal')
    # check_purchase_internal = fields.Boolean("Check Internal Purchase", compute='_compute_state_purchase_internal')

    def _compute_state_purchase(self):
        for rec in self:
            purchases = self.env['purchase.order'].search([('origin', '=', rec.name)])
            internal_pickings = self.env['stock.picking'].search([('origin', '=', rec.name)])
            p_flag = 0
            i_flag = 0
            if purchases:
                for i in purchases:
                    if not i.state == 'purchase':
                        p_flag = 1
            if internal_pickings:
                for j in internal_pickings:
                    if not j.state == 'done':
                        i_flag = 1
            if purchases or internal_pickings:
                if i_flag == 0 and p_flag == 0:
                    rec.check_purchases = True
                else:
                    rec.check_purchases = False
            else:
                rec.check_purchases = False

    # def _compute_state_purchase(self):
    #     for rec in self:
    #         purchases = self.env['purchase.order'].search([('state', '=', 'purchase'), ('origin', '=', rec.name)])
    #         if purchases:
    #             rec.check_purchases = True
    #         else:
    #             rec.check_purchases = False
    #
    # def _compute_state_internal(self):
    #     for rec in self:
    #         internal_pickings = self.env['stock.picking'].search([('state', '=', 'done'), ('origin', '=', rec.name)])
    #         print(internal_pickings)
    #         if internal_pickings:
    #             rec.check_internal = True
    #         else:
    #             rec.check_internal = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(MaterialRequisitioninh, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if self.env.user.has_group('material_purchase_requisitions.group_purchase_requisition_user'):
            temp = etree.fromstring(result['arch'])
            temp.set('create', '0')
            temp.set('edit', '0')
            result['arch'] = etree.tostring(temp)
        if self.env.user.has_group('sanadbags_requisition.group_requisition_user'):
            temp = etree.fromstring(result['arch'])
            temp.set('create', '1')
            temp.set('edit', '1')
            result['arch'] = etree.tostring(temp)
        else:
            temp = etree.fromstring(result['arch'])
            temp.set('create', '0')
            temp.set('edit', '0')
            result['arch'] = etree.tostring(temp)
        return result

    def action_show_po(self):
        for rec in self:
            tree_view_id = self.env.ref('sanadbags_requisition.purchase_order_tree_req').ids
            form_view_id = self.env.ref('sanadbags_requisition.purchase_order_form_req').ids
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase',
                'views': [[tree_view_id, 'tree'], [form_view_id, 'form']],
                'domain': [('origin', '=', rec.name)],
                'target': 'current',
                'res_model': 'purchase.order',
                'view_mode': 'tree,form',
            }
    # def action_received(self):
    #     for rec in self:
    #         purchases = self.env['purchase.order'].search([('state', '=', 'purchase')])
    #         if purchases:


    def show_picking(self):
        for rec in self:
            tree_view_id = self.env.ref('sanadbags_requisition.vpicktree_req').ids
            form_view_id = self.env.ref('sanadbags_requisition.view_picking_form_req').ids
            return {
                'type': 'ir.actions.act_window',
                'name': 'Purchase',
                'views': [[tree_view_id, 'tree'], [form_view_id, 'form']],
                'domain': [('origin', '=', rec.name)],
                'target': 'current',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
            }

    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('internal', 'Internal Picking Created'),
        ('stock_internal', 'Purchase & Picking Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        track_visibility='onchange',
    )

    @api.model
    def default_get_picking(self):
        search = self.env['stock.picking.type'].search([('code', '=', 'internal')])
        return search

    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
        default=default_get_picking

    )

    def request_stock(self):
        record = super(MaterialRequisitioninh, self).request_stock()
        i = 0
        p = 0
        for rec in self.requisition_line_ids:
            if rec.requisition_type == 'internal':
                i = i + 1
            if rec.requisition_type == 'purchase':
                p = p + 1

        if i > 0 and p > 0:
            self.state = 'stock_internal'
        elif i > 0 and p == 0:
            self.state = 'internal'
        elif i == 0 and p > 0:
            self.state = 'stock'
        return record


class MaterialRequisition(models.Model):
    _inherit = 'material.purchase.requisition.line'

    @api.onchange('product_id')
    def test_action(self):
        partner_users = self.env['res.users'].search([]).mapped('partner_id')
        partner_list = []
        for users in partner_users:
            obj = self.env['res.users'].search([('partner_id', '=', users.id)])
            if obj.has_group('purchase.group_purchase_user'):
                partner_list.append(obj.id)
        return {'domain': {'partner_id': [('id', 'in', partner_list)]
                           }}

    @api.onchange('requisition_type', 'product_id', 'uom', 'qty')
    def hide_add_lines(self):
        for rec in self.requisition_id:
            if rec.state not in 'draft':
                raise UserError('This cannot be done')




