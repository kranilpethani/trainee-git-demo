from odoo import fields, models, api, _

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    master_bom = fields.Boolean()

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered(lambda r: r.master_bom)._unset_other_master()
        return records

    def write(self, vals):
        res = super().write(vals)
        if vals.get('master_bom'):
            self._unset_other_master()
        return res

    def _unset_other_master(self):
        for rec in self:
            boms = self.search([
                ('id', '!=', rec.id),
                ('master_bom', '=', True),
                '|',
                ('product_id', '=', rec.product_id.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id)
            ])
            boms.write({'master_bom': False})