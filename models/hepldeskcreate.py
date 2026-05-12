from odoo import models, api

class HelpdeskCreateFsmTask(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'

    def _generate_task_values(self):
        vals = super()._generate_task_values()

        ticket = self.helpdesk_ticket_id

        if ticket.product_type:
            user = self.env['res.users'].search([
                ('service_type', '=', ticket.product_type)
            ], limit=1)

            if user:
                vals['user_ids'] = [(6, 0, [user.id])]
                vals['planned_date_begin'] = ticket.date
        return vals