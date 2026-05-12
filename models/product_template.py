from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    special_item = fields.Boolean()