# -*- coding: utf-8 -*-
# from odoo import http


# class Attacthments(http.Controller):
#     @http.route('/attacthments/attacthments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attacthments/attacthments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('attacthments.listing', {
#             'root': '/attacthments/attacthments',
#             'objects': http.request.env['attacthments.attacthments'].search([]),
#         })

#     @http.route('/attacthments/attacthments/objects/<model("attacthments.attacthments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attacthments.object', {
#             'object': obj
#         })
