# -*- coding: utf-8 -*-
# ©  2008-2018 Fekete Mihai <mihai.fekete@forbiom.eu>
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Stock Location
# ----------------------------------------------------------


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = "stock.location"

    usage = fields.Selection(selection_add=[('in_custody', 'In Custody'),
                                            ('usage_giving', 'Usage Giving'),
                                            ('consume', 'Consume')],

                             help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                       \n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations
                       \n* In Custody: Virtual location for products received in custody
                       \n* Usage Giving: Virtual location for products given in usage
                       \n* In Custody: Virtual location for products consumed beside production.
                      """, index=True)

    merchandise_type = fields.Selection([("store", "Store"), ("warehouse", "Warehouse")], string="Merchandise type",
                                        default="warehouse")

    # locatiile sunt dependente de companie. de ce urmatoarele campuri sunt si ele depdenente de companie ?
    # campul standard valuation_in_account_id nu este company_dependent
    # property_stock_account_input_location_id = fields.Many2one('account.account',
    #                                                            string='Stock Input Account',
    #                                                            help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
    #                                                                 "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used.",
    #                                                            company_dependent=True)
    # campul standard este valuation_out_account_id
    # property_stock_account_output_location_id = fields.Many2one('account.account',
    #                                                             string='Stock Output Account',
    #                                                             help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
    #                                                                  "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used.",
    #                                                             company_dependent=True)
    property_account_creditor_price_difference_location_id = fields.Many2one(
        'account.account',
        string="Price Difference Account",
        help="This account will be used to value price difference between purchase price and cost price.",
        company_dependent=True)
    property_account_income_location_id = fields.Many2one(
        'account.account',
        string="Income Account",
        help="This account will be used to value outgoing stock using sale price.",
        company_dependent=True)
    property_account_expense_location_id = fields.Many2one(
        'account.account',
        string="Expense Account",
        help="This account will be used to value outgoing stock using cost price.",
        company_dependent=True)