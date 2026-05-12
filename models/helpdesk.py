from odoo import fields, models, api, _


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_type = fields.Selection([
        ('installation' , 'Installation'),
        ('repair' ,'Repair'),
        ('amc_service','AMC Service')])

    product_type = fields.Selection([
        ('ac' , 'AC'),
        ('washing_machine' ,'Washing Machine'),
        ('fridge' ,'Fridge')])

    brand = fields.Selection([
        ('lg' , 'LG'),
        ('sony' ,'Sony'),
        ('godrej' ,'Godrej')])

    warranty_status =fields.Selection([
        ('in_warranty' , 'IN Warranty'),
        ('expired' ,'Expired')])

    date = fields.Datetime()

