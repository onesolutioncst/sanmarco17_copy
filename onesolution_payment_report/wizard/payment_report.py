# ©  2008-2021 Onesolution
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models


class PaymentReport(models.TransientModel):
    _name = "account.payment.report"
    _description = "PaymentReport"

    date_from = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_to = fields.Date(string="End Date", required=True, default=fields.Date.today)
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, required=True)
    journal_payment_ids = fields.Many2many(
        "account.journal", domain=[("type", "in", ["cash", "bank"])], string="Payment Journal"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        journals = self.env["account.journal"].search([("type", "in", ["cash", "bank"])])
        res["journal_payment_ids"] = [(6, 0, journals.ids)]
        return res

    def do_compute(self):
        all_payments = self.env["account.payment"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("payment_type", "=", "inbound"),
                ("partner_type", "=", "customer"),
                ("state", "in", ["posted", "reconciled"]),
                ("journal_id", "in", self.journal_payment_ids.ids),
            ]
        )

        lines = []
        for payment in all_payments:
            if payment.reconciled_invoice_ids:
                for invoice in payment.reconciled_invoice_ids:
                    payments_widget_value = invoice.invoice_payments_widget
                    if payments_widget_value:
                        payments_widget_list = payments_widget_value['content']
                        for payments_widget in payments_widget_list:
                            lines.append(
                                {
                                    "report_id": self.id,
                                    "account_payment_id": payments_widget['account_payment_id'],
                                    "payment_date": payments_widget['date'],
                                    "partner_id": invoice.partner_id.id,
                                    "amount": payment.amount,
                                    "currency_id": payments_widget['currency_id'],
                                    "payment_journal_id": payment.journal_id.id,
                                    "payment_method_id": payment.payment_method_id.id,
                                    "invoice_journal_id": invoice.journal_id.id,
                                    "account_move_id": invoice.id,
                                    "account_amount_total": invoice.amount_total,
                                    "account_amount_paid": payments_widget['amount'],
                                    "account_amount_duo": invoice.amount_residual,
                                }
                            )
        self.env["account.payment.report.line"].create(lines)

    def button_show_report(self):
        self.do_compute()
        action = self.env.ref("onesolution_payment_report.action_account_payment_report_line").read()[0]
        action["display_name"] = "{} ({}-{})".format(
            action["name"],
            self.date_from,
            self.date_to,
        )
        action["domain"] = [("report_id", "=", self.id)]
        action["context"] = {
            "active_id": self.id,
            # "general_buttons": self.env["account.payment.report.line"].get_general_buttons(),
        }
        action["target"] = "main"
        return action

    def print_pdf(self):
        action_report = self.env.ref("onesolution_payment_report.action_account_payment_report_line")
        return action_report.report_action(self, config=False)


class PaymentReportLine(models.TransientModel):
    _name = "account.payment.report.line"
    _description = "PaymentReportLine"

    report_id = fields.Many2one("account.payment.report")
    payment_date = fields.Date(string="Date")
    partner_id = fields.Many2one("res.partner", string="Customer")
    amount = fields.Monetary(string="Payment Amount")
    currency_id = fields.Many2one("res.currency")
    payment_journal_id = fields.Many2one("account.journal")
    payment_journal_type = fields.Selection(related="payment_journal_id.type", store=True)
    invoice_journal_id = fields.Many2one("account.journal")
    account_move_id = fields.Many2one("account.move")
    account_amount_total = fields.Float("Account amount Total")
    account_amount_duo = fields.Float("Account Amount Due")
    account_amount_paid = fields.Float("Account Amount Paid")
    account_payment_id = fields.Many2one("account.payment")
    payment_method_id = fields.Many2one("account.payment.method", string="Payment Method")

    def get_general_buttons(self):
        return [
            {
                "action": "print_pdf",
                "name": _("Print Preview"),
                "model": "account.payment.report",
            }
        ]
