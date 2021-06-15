# -*- coding: utf-8 -*-
# from odoo import http


# class CrmFieldsAdd(http.Controller):
#     @http.route('/crm_fields_add/crm_fields_add/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_fields_add/crm_fields_add/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_fields_add.listing', {
#             'root': '/crm_fields_add/crm_fields_add',
#             'objects': http.request.env['crm_fields_add.crm_fields_add'].search([]),
#         })

#     @http.route('/crm_fields_add/crm_fields_add/objects/<model("crm_fields_add.crm_fields_add"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_fields_add.object', {
#             'object': obj
#         })
