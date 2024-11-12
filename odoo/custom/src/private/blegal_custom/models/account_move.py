# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_base_import_pdf_by_template_reprocess(self):
        items = self.browse(self.env.context.get("active_ids"))
        if any(not move.is_invoice(include_receipts=True) for move in items):
            raise UserError(_("Only invoices can be reprocessed."))
        if any(move.state != "draft" for move in items):
            raise UserError(_("Only draft invoices can be reprocessed."))
        for move in items:
            attachment_pdf = fields.first(
                move.attachment_ids.filtered(lambda x: ".pdf" in x.name)
            )
            if attachment_pdf:
                move.invoice_line_ids.unlink()  # Remove all lines first
                wizard = self.env["wizard.base.import.pdf.upload"].create(
                    {
                        "model": move._name,
                        "record_ref": f"{move._name},{move.id}",
                        "attachment_ids": [(6, 0, attachment_pdf.ids)],
                    }
                )
                wizard.action_process()
