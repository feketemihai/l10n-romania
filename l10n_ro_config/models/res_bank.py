# coding=utf-8
from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp



class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    footer =  fields.Boolean("Display on Reports", default=True,
                             help="Display this bank account on the footer of printed documents like invoices and sales orders.")