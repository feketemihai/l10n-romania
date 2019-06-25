# Copyright (C) 2018 FOREST AND BIOMASS ROMANIA SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class RomaniaTrialBalanceReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * RomaniaTrialBalanceReport
    ** RomaniaTrialBalanceReportAccount
    """

    _name = 'l10n_ro_report_trial_balance'

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()

    only_posted_moves = fields.Boolean()
    hide_account_without_move = fields.Boolean()
    with_special_accounts = fields.Boolean()
    company_id = fields.Many2one('res.company')
    account_ids = fields.Many2many('account.account')

    # Data fields, used to browse report data
    line_account_ids = fields.One2many('l10n_ro_report_trial_balance_account', inverse_name='report_id')


    col_opening_balance = fields.Boolean('Balance Opening Year', default=True)  # solduri initiale an
    col_opening = fields.Boolean('Opening Year', default=False)  # rulaje la inceput de an
    col_initial_balance = fields.Boolean('Balance Initial period', default=False)  # solduri initiale perioada
    col_initial = fields.Boolean('Initial period', default=False)  # sume perecente
    col_period = fields.Boolean('Period', default=True)  # rulaje perioada

    col_cumulative = fields.Boolean('Cumulative', default=True)         # total rulaje (de la inceputul anului)

    col_total = fields.Boolean('Total amount', default=True)  # sume totale
    col_balance = fields.Boolean('Balance', default=True)  # solduri finale

    refresh_report = fields.Boolean('Refresh Report')

class RomaniaTrialBalanceAccountReport(models.TransientModel):
    _name = 'l10n_ro_report_trial_balance_account'
    _order = 'code ASC, name ASC'

    report_id = fields.Many2one('l10n_ro_report_trial_balance', ondelete='cascade', index=True)

    # Data fields, used to keep link with real object
    account_id = fields.Many2one('account.account', index=True, string='Account')

    account_group_id = fields.Many2one('account.group', index=True)

    # Data fields, used for report display
    code = fields.Char()
    name = fields.Char()

    # solduri initiale
    debit_opening_balance = fields.Float(digits=(16, 2))
    credit_opening_balance = fields.Float(digits=(16, 2))

    # rulaje intiale
    debit_opening = fields.Float(digits=(16, 2))
    credit_opening = fields.Float(digits=(16, 2))

    # solduri initiale perioada
    debit_initial_balance = fields.Float(digits=(16, 2))
    credit_initial_balance = fields.Float(digits=(16, 2))

    # sume perecente
    debit_initial = fields.Float(digits=(16, 2))
    credit_initial = fields.Float(digits=(16, 2))

    # rulaje perioada
    debit = fields.Float(digits=(16, 2))
    credit = fields.Float(digits=(16, 2))

    # Rulaje cumulate
    debit_cumulative = fields.Float(digits=(16, 2))
    credit_cumulative = fields.Float(digits=(16, 2))

    # sume totale
    debit_total = fields.Float(digits=(16, 2))
    credit_total = fields.Float(digits=(16, 2))

    # solduri finale
    debit_balance = fields.Float(digits=(16, 2))
    credit_balance = fields.Float(digits=(16, 2))

    # Data fields, used to browse report data
    account_ids = fields.Many2many(comodel_name='account.account',string='Accounts')


class RomaniaTrialBalanceComputeReport(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'l10n_ro_report_trial_balance'


    def get_reports_buttons(self):
        return [{'name': _('Print Preview'), 'action': 'print_pdf'}, {'name': _('Export (XLSX)'), 'action': 'print_xlsx'}]


    @api.multi
    def print_pdf(self):
        return self.print_report('qweb-pdf')

    @api.multi
    def print_xlsx(self):
        return self.print_report('xlsx')

    @api.multi
    def print_report(self, report_type='qweb'):
        self.ensure_one()
        context = dict(self.env.context)
        if report_type == 'xlsx':
            report_name = 'l10n_ro_report_trial_balance_xlsx'
        else:
            report_name = 'l10n_ro_report_trial_balance.l10n_ro_report_trial_balance_qweb'
        action = self.env['ir.actions.report'].search(
            [('report_name', '=', report_name),
             ('report_type', '=', report_type)], limit=1)
        return action.with_context(context).report_action(self)


    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get('active_id'))
        if report:
            action =  self.env.ref('l10n_ro_report_trial_balance.action_l10n_ro_report_trial_balance_control')
            html = action.render_qweb_html( report.ids)
            result['html'] = html[0]

        return result



    # def _get_html(self):
    #     result = {}
    #     rcontext = {}
    #     context = dict(self.env.context)
    #     report = self.browse(context.get('active_id'))
    #     if report:
    #         rcontext['o'] = report
    #         result['html'] = self.env.ref('l10n_ro_report_trial_balance.l10n_ro_report_trial_balance').render(rcontext)
    #     return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()



    @api.multi
    def do_execute(self):
        self.ensure_one()
        domain = [
            ('date_from', '=', self.date_from),
            ('date_to', '=', self.date_to),
            ('id', '!=', self.id)
        ]
        if self.refresh_report:
            report = self.search(domain)
            report.unlink()
            report = False
        else:
            report = self.search(domain, limit=1)
            if report:
                report.write({
                    'hide_account_without_move': self.hide_account_without_move,
                    'with_special_accounts': self.with_special_accounts,
                    'col_opening_balance': self.col_opening_balance,
                    'col_opening': self.col_opening,
                    'col_initial_balance': self.col_initial_balance,
                    'col_initial': self.col_initial,
                    'col_period': self.col_period,
                    'col_cumulative': self.col_cumulative,
                    'col_total': self.col_total,
                    'col_balance': self.col_balance,
                })

        if not report:
            self.compute_data_for_report()
            report = self

        return report


    @api.multi
    def compute_data_for_report(self):

        self.ensure_one()
        self._inject_account_lines()
        self._compute_account_group_values()
        # Refresh cache because all data are computed with SQL requests
        self.refresh()

    def _inject_account_lines(self):
        """Inject report values for report_trial_balance_account"""
        date_from = fields.Date.from_string(self.date_from)
        fy_start_date = fields.Date.to_string(date_from + relativedelta(day=1, month=1))
        if self.only_posted_moves:
            states = "'posted'"
        else:
            states = "'draft', 'posted'"
        if self.account_ids:
            accounts = self.account_ids
        else:
            accounts = self.env['account.account'].search([('company_id', '=', self.company_id.id)])

        if not self.with_special_accounts:
            sp_acc_type = self.env.ref('l10n_ro.data_account_type_not_classified')
            if sp_acc_type:
                accounts = accounts.filtered(lambda a: a.user_type_id.id != sp_acc_type.id)
        query_inject_account = """
                INSERT INTO
                    l10n_ro_report_trial_balance_account
                    (
                    report_id,
                    create_uid,
                    create_date,
                    account_id,
                    code,
                    name,
                    
                    debit_opening_balance,
                    credit_opening_balance,
                    debit_opening,
                    credit_opening,
                    
                    debit_initial_balance,
                    credit_initial_balance,    
                                   
                    debit_initial,
                    credit_initial,
                    
                    debit,
                    credit,
                  
                    debit_cumulative,
                    credit_cumulative,
                    
                    debit_total,
                    credit_total,
                    
                    debit_balance,
                    credit_balance
                    
                    )
                SELECT 
                    %s AS report_id,
                    %s AS create_uid,
                    NOW() AS create_date,
                    subselect.id as account_id,
                    subselect.code,
                    subselect.name,
                    
                    subselect.debit_opening_balance,
                    subselect.credit_opening_balance,
                    
                    subselect.debit_opening,
                    subselect.credit_opening,
                    
                    subselect.debit_initial_balance,
                    subselect.credit_initial_balance,
                    
                    subselect.debit_initial,
                    subselect.credit_initial,
                    
                    subselect.debit,
                    subselect.credit,
                    
                    debit_initial + debit as debit_cumulative,
                    credit_initial + credit as credit_cumulative,   
                                  
                    debit_opening_balance + debit_initial + debit as debit_total,
                    credit_opening_balance + credit_initial + credit as credit_total,                       

                    subselect.debit_balance,
                    subselect.credit_balance
                    
                    
                FROM (
                SELECT
                   
                    accounts.*,
                    
                    CASE WHEN accounts.debit_opening > accounts.credit_opening
                        THEN accounts.debit_opening - accounts.credit_opening
                        ELSE 0
                    END AS debit_opening_balance,
                    CASE WHEN accounts.credit_opening > accounts.debit_opening
                        THEN accounts.credit_opening - accounts.debit_opening
                        ELSE 0
                    END AS credit_opening_balance,
                    
                    CASE WHEN accounts.debit_initial > accounts.credit_initial
                        THEN accounts.debit_initial - accounts.credit_initial
                        ELSE 0
                    END AS debit_initial_balance,
                    CASE WHEN accounts.credit_initial > accounts.debit_initial
                        THEN accounts.credit_initial - accounts.debit_initial
                        ELSE 0
                    END AS credit_initial_balance,
                    
                    CASE WHEN accounts.debit_total > accounts.credit_total
                        THEN accounts.debit_total - accounts.credit_total
                        ELSE 0
                    END AS debit_balance,
                    CASE WHEN accounts.credit_total > accounts.debit_total
                        THEN accounts.credit_total - accounts.debit_total
                        ELSE 0
                    END AS credit_balance

                FROM
                    (
                    SELECT
                        acc.id, acc.code, acc.name,
                        coalesce(sum(open.debit),0) AS debit_opening,
                        coalesce(sum(open.credit),0) AS credit_opening,
                        coalesce(sum(init.debit),0) AS debit_initial,
                        coalesce(sum(init.credit),0) AS credit_initial,
                        coalesce(sum(current.debit),0) AS debit,
                        coalesce(sum(current.credit),0) AS credit,
                        
                        coalesce(sum(open.debit),0) + coalesce(sum(init.debit),0) +
                            coalesce(sum(current.debit),0) AS debit_total,
                        coalesce(sum(open.credit),0) + coalesce(sum(init.credit),0) +
                            coalesce(sum(current.credit),0) AS credit_total
                    FROM
                        account_account acc
                        LEFT OUTER JOIN account_move_line AS open
                            ON open.account_id = acc.id AND open.date < %s
                        LEFT OUTER JOIN account_move_line AS init
                            ON init.account_id = acc.id AND init.date >= %s AND init.date < %s
                        LEFT OUTER JOIN account_move_line AS current
                            ON current.account_id = acc.id AND current.date >= %s
                                AND current.date <= %s
                        LEFT JOIN account_move AS move
                            ON open.move_id = move.id AND move.state in (%s)
                        LEFT JOIN account_move AS init_move
                            ON init.move_id = init_move.id AND init_move.state in (%s)
                        LEFT JOIN account_move AS current_move
                            ON current.move_id = current_move.id AND current_move.state in (%s)
                    WHERE acc.id in %s
                    GROUP BY acc.id
                    ORDER BY acc.code) as accounts
                ) as subselect
        """


        query_inject_account_params = (
            self.id,
            self.env.uid,
            str(fy_start_date),
            str(fy_start_date), str(self.date_from),
            str(self.date_from), str(self.date_to),
            states,
            states,
            states,
            accounts._ids,
        )
        self.env.cr.execute(query_inject_account, query_inject_account_params)
        # if self.hide_account_balance_at_0:
        #     lines = self.line_account_ids.filtered(lambda a: a.debit_balance == 0 and a.credit_balance == 0)
        #     lines.unlink()

    def _compute_account_group_values(self):
        if not self.account_ids:
            acc_res = self.line_account_ids
            groups = self.env['account.group'].search([('code_prefix', '!=', False)])
            for group in groups:
                accounts = acc_res.filtered(lambda a: a.account_id.id in group.compute_account_ids.ids)
                # if self.hide_account_balance_at_0:
                #     accounts = accounts.filtered(lambda a: a.debit_balance != 0 or a.credit_balance != 0)
                if accounts:
                    newdict = {
                        'report_id': self.id,
                        'account_group_id': group.id,
                        'code': group.code_prefix,
                        'name': group.name,

                        'debit_opening_balance': sum(acc.debit_opening_balance for acc in accounts),
                        'credit_opening_balance': sum(acc.credit_opening_balance for acc in accounts),

                        'debit_opening': sum(acc.debit_opening for acc in accounts),
                        'credit_opening': sum(acc.credit_opening for acc in accounts),

                        'debit_initial_balance': sum(acc.debit_initial_balance for acc in accounts),
                        'credit_initial_balance': sum(acc.credit_initial_balance for acc in accounts),

                        'debit_initial': sum(acc.debit_initial for acc in accounts),
                        'credit_initial': sum(acc.credit_initial for acc in accounts),
                        'debit': sum(acc.debit for acc in accounts),
                        'credit': sum(acc.credit for acc in accounts),

                        'debit_cumulative': sum(acc.debit_cumulative for acc in accounts),
                        'credit_cumulative': sum(acc.credit_cumulative for acc in accounts),

                        'debit_total': sum(acc.debit_total for acc in accounts),
                        'credit_total': sum(acc.credit_total for acc in accounts),
                        'debit_balance': sum(acc.debit_balance for acc in accounts),
                        'credit_balance': sum(acc.credit_balance for acc in accounts),
                    }
                    self.env['l10n_ro_report_trial_balance_account'].create(newdict)
