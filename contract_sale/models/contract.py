# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice=date_invoice, journal=journal
        )
        if invoice_vals.get("invoice_user_id"):
            user = self.env["res.users"].browse(invoice_vals.get("invoice_user_id"))
            invoice_vals.update(team_id=user.sale_team_id.id)
        return invoice_vals, move_form
