from odoo import fields, models

class ConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    min = fields.Float()
    max = fields.Float()
    product_id = fields.Many2one('product.product')
    times = fields.Float("Hours")

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('custom.min', self.min or 0)
        self.env['ir.config_parameter'].sudo().set_param('custom.max', self.max or 0)
        self.env['ir.config_parameter'].sudo().set_param('custom.product_id', self.product_id.id or 0)
        self.env['ir.config_parameter'].sudo().set_param('custom.times', self.times or 0)

    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        product_param = params.get_param('custom.product_id')

        product_id = False
        if product_param and product_param.isdigit():
            product_id = int(product_param)
        res.update(
            min=int(float(params.get_param('custom.min', 0))),
            max=int(float(params.get_param('custom.max', 0))),
            product_id=product_id,
            times=float(params.get_param('custom.times', 0)),
        )
        return res