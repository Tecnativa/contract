# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_portal_published = fields.Boolean(
        compute="_compute_is_portal_published",
        inverse="_inverse_is_portal_published",
        string="Published in portal?",
    )

    @api.depends("line_ids.analytic_distribution", "message_partner_ids")
    def _compute_is_portal_published(self):
        for move in self:
            partner_ids = move._get_analytic_partner_ids()
            move.is_portal_published = bool(
                partner_ids.intersection(move.message_partner_ids.ids)
            )

    def _inverse_is_portal_published(self):
        for move in self:
            partner_ids = list(move._get_analytic_partner_ids())
            if move.is_portal_published and not partner_ids:
                raise UserError(
                    _(
                        "This invoice can't be published to the portal "
                        "because the analytic distribution has no customer set."
                    )
                )
            if move.is_portal_published:
                move.message_subscribe(partner_ids=partner_ids)
            else:
                move.message_unsubscribe(partner_ids=partner_ids)

    def _get_analytic_partner_ids(self):
        partner_ids = set()
        AnalyticAccount = self.env["account.analytic.account"]
        for line in self.line_ids.filtered("analytic_distribution"):
            for analytic_account_id in line.analytic_distribution:
                analytic_account = AnalyticAccount.browse(int(analytic_account_id))
                if analytic_account.partner_id:
                    partner_ids.add(analytic_account.partner_id.id)
        return partner_ids

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
