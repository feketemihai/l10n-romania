# Copyright (C) 2014 Forest and Biomass Romania
# Copyright (C) 2020 NextERP Romania
# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"



    @api.constrains(
        "property_stock_valuation_account_id",
        "property_stock_account_output_categ_id",
        "property_stock_account_input_categ_id",
    )
    def _check_valuation_accouts(self):
        """ Overwrite default constraint for Romania,
        stock_valuation, stock_output and stock_input
        are the same
        """
        ro_chart = self.env["ir.model.data"].get_object_reference(
            "l10n_ro", "ro_chart_template"
        )[1]
        if self.env.company.chart_template_id.id == ro_chart:
            return
        else:
            self.super(ProductCategory, self)._check_valuation_accouts()



class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_stock_valuation_account_id = fields.Many2one(
        "account.account",
        "Stock Valuation Account",
        company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]),"
               "('deprecated', '=', False)]",
        check_company=True,
        help="In Romania accounting is only one account for valuation/input/"
             "output. If this value is set, we will use it, otherwise will "
             "use the category value. ",
    )


    def _get_product_accounts(self):

        accounts = super(ProductTemplate, self)._get_product_accounts()

        property_stock_valuation_account_id = (
            self.property_stock_valuation_account_id
            or self.categ_id.property_stock_valuation_account_id
        )
        if property_stock_valuation_account_id:
            accounts.update(
                {
                    # "stock_input": property_stock_valuation_account_id,
                    # "stock_output": property_stock_valuation_account_id,
                    "stock_valuation": property_stock_valuation_account_id,
                }
            )
        if self.env.context.get('notice', False):
            stock_picking_payable_account_id = self.env.user.company_id.property_stock_picking_payable_account_id
            if stock_picking_payable_account_id:
                accounts.update({
                    "stock_input":stock_picking_payable_account_id
                })

        # la vanzare se scoate stocul pe cheltuiala
        if self.env.context.get('sale', False):
            accounts.update({
                "stock_output":accounts['expense']
            })

        return accounts