from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    invoice_id = fields.Many2one("account.move", string="Invoice")

    def action_set_sold(self):
        self.check_access_rights("write")
        self.check_access_rule("write")
        AccountMove = self.env["account.move"].sudo()
        journal = AccountMove.with_context(
            default_move_type="out_invoice"
        )._get_default_journal()
        values = {
            "partner_id": self.partner_id.id,
            "move_type": "out_invoice",
            "journal_id": journal.id,
            "invoice_line_ids": [
                (
                    # adds a new record created from the provided value dict.
                    0,
                    0,
                    {
                        "name": self.name,
                        "quantity": 1.0,
                        "price_unit": 0.06 * self.selling_price,
                    },
                ),
                (
                    # adds a new record created from the provided value dict.
                    0,
                    0,
                    {
                        "name": "Administrative Fees",
                        "quantity": 1.0,
                        "price_unit": 100.00,
                    },
                ),
            ],
        }
        self.invoice_id = AccountMove.create(values)
        return super().action_set_sold()
