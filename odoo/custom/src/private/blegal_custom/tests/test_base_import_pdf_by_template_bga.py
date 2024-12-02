# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from .common import TestBaseImportPdfByTemplateBase


class TestBaseImportPdfByTemplateBga(TestBaseImportPdfByTemplateBase):
    def test_account_invoice_bga_taaf(self):
        self._set_template_values("account_move_taaf")
        attachment = self._create_ir_attachment("bga/account-move-taaf.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "2024/1/2651")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 1))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 208.03)

    def test_account_invoice_bga_tennablia(self):
        self._set_template_values("account_move_tennablia")
        attachment = self._create_ir_attachment("bga/account-move-tennablia.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "24")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 2))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 1550)

    def test_account_invoice_bga_wanme(self):
        self._set_template_values("account_move_wanme")
        attachment = self._create_ir_attachment("bga/account-move-wanme.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "#2024-PV-0808")
        self.assertEqual(record.invoice_date, datetime.date(2024, 8, 2))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 9.99)
