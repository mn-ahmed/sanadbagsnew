# -*- coding: utf-8 -*-
# from odoo import http


# class FieldAttacthments(http.Controller):
#     @http.route('/field_attacthments/field_attacthments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_attacthments/field_attacthments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_attacthments.listing', {
#             'root': '/field_attacthments/field_attacthments',
#             'objects': http.request.env['field_attacthments.field_attacthments'].search([]),
#         })

#     @http.route('/field_attacthments/field_attacthments/objects/<model("field_attacthments.field_attacthments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_attacthments.object', {
#             'object': obj
#         })
