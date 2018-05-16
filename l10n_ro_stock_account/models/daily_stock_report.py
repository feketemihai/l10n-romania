# coding=utf-8
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class DailyStockReport(models.TransientModel):
    _name = 'l10n_ro_daily_stoc_report'

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    location_id = fields.Many2one('stock.location', store=True, compute='_compute_stock_location_id')

    @api.multi
    def do_compute(self):
        self.env['account.move.line'].check_access_rights('read')
        stock_init = {}
        stock_in = {}
        stock_out = {}

        to_date = self.date_from
        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id)
                        FROM account_move_line AS aml
                            WHERE aml.product_id IS NOT NULL AND 
                                    aml.company_id=%s AND 
                                    aml.date < %s AND 
                                    stock_location_id = %s
                            GROUP BY aml.product_id, aml.account_id """
        params = (self.env.user.company_id.id, to_date, self.location_id.id)

        self.env.cr.execute(query, params=params)

        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_init[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products = self.env['product.product'].browse(product_ids)

        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id) 
                         FROM account_move_line AS aml
                              WHERE aml.product_id IS NOT NULL AND 
                                       aml.company_id=%s AND 
                                       aml.date >= %s AND ml.date  <= %s
                                       stock_location_id = %s 
                                       quantity >= 0 
                              GROUP BY aml.product_id, aml.account_id"""
        params = (self.env.user.company_id.id, self.date_from, self.date_to, self.location_id.id)

        self.env.cr.execute(query, params=params)
        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_in[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products |= self.env['product.product'].browse(product_ids)

        query = """SELECT aml.product_id, aml.account_id, sum(aml.debit) - sum(aml.credit), sum(quantity), array_agg(aml.id) 
                                 FROM account_move_line AS aml
                                      WHERE aml.product_id IS NOT NULL AND 
                                               aml.company_id=%s AND 
                                               aml.date >= %s AND ml.date  <= %s
                                               stock_location_id = %s 
                                               quantity < 0 
                                      GROUP BY aml.product_id, aml.account_id"""
        params = (self.env.user.company_id.id, self.date_from, self.date_to, self.location_id.id)

        self.env.cr.execute(query, params=params)
        product_ids = []
        res = self.env.cr.fetchall()
        for row in res:
            product_ids += [row[0]]
            stock_out[(row[0], row[1])] = (row[2], row[3], list(row[4]))
        products |= self.env['product.product'].browse(product_ids)

        for product in products:
            valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
            value, quantity, aml_ids = stock_init.get((product.id, valuation_account_id)) or (0, 0, [])
            self.env['l10n_ro_daily_stoc_report.line'].create({
                'report_id': self.id,
                'product_id': product.id,
                'quantity': quantity,
                'amount': value,
                'type': 'sold',
            })

            value, quantity, aml_ids = stock_in.get((product.id, valuation_account_id)) or (0, 0, [])
            self.env['l10n_ro_daily_stoc_report.line'].create({
                'report_id': self.id,
                'product_id': product.id,
                'quantity': quantity,
                'amount': value,
                'type': 'in',
            })

            value, quantity, aml_ids = stock_in.get((product.id, valuation_account_id)) or (0, 0, [])
            self.env['l10n_ro_daily_stoc_report.line'].create({
                'report_id': self.id,
                'product_id': product.id,
                'quantity': quantity,
                'amount': value,
                'type': 'out',
            })


class DailyStockReportLine(models.TransientModel):
    _name = 'l10n_ro_daily_stoc_report.line'

    report_id = fields.Many2one('l10n_ro_daily_stoc_report')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    amount = fields.Monetary()
    type = fields.selection([('sold', 'Sold'), ('in', 'Input'), ('out', 'Output')])
    aml_ids = fields.Many2many('account.move.line')
