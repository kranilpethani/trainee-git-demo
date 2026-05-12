from odoo import fields, models, api, _

class ServiceTechnician(models.Model):
    _inherit = 'res.users'

    service_type = fields.Selection([
        ('ac', 'AC'),
        ('washing_machine', 'Washing Machine'),
        ('fridge', 'Fridge')
    ], string="Service Type")
