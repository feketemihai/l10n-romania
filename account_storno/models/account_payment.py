from odoo import models, api

# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': 1,
    'out_refund': 1,
}

class AccountRegisterPayment(models.TransientModel):
    _inherit = 'account.register.payments'

    @api.model
    def _compute_payment_amount(self, invoice_ids):
        payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoice_ids and invoice_ids[0].currency_id

        total = 0
        for inv in invoice_ids:
            if inv.currency_id == payment_currency:
                total += MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] * inv.residual_signed
            else:
                amount_residual = inv.company_currency_id.with_context(date=self.payment_date).compute(
                    inv.residual_company_signed, payment_currency)
                total += MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] * amount_residual
        return total
