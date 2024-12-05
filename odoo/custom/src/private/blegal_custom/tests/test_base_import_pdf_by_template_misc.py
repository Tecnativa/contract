# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from .common import TestBaseImportPdfByTemplateBase


class TestBaseImportPdfByTemplateMisc(TestBaseImportPdfByTemplateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creinsa
        cls._set_template_values("account_move_creinsa")
        cls.attachment_creinsa = cls._create_ir_attachment(
            "misc/account-move-creinsa.pdf"
        )

    def test_account_invoice_aws(self):
        self._set_template_values("account_move_aws")
        attachment = self._create_ir_attachment("misc/account-move-aws.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "EUINES24-84613")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 2))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 18.34)

    def _test_account_invoice_creinsa_data(self, record):
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "242164")
        self.assertEqual(record.invoice_date, datetime.date(2024, 8, 1))
        self.assertEqual(record.partner_id, self.partner)
        self.assertIn(self.product, record.mapped("invoice_line_ids.product_id"))
        self.assertEqual(len(record.invoice_line_ids), 17)
        self.assertEqual(sum(record.invoice_line_ids.mapped("quantity")), 18)

    def test_account_invoice_creinsa(self):
        wizard = self._create_wizard_base_import_pdf_upload(self.attachment_creinsa)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(self.attachment_creinsa, record.attachment_ids)
        self._test_account_invoice_creinsa_data(record)

    def test_action_base_import_pdf_by_template_reprocess(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "journal_id": self.journal.id,
            }
        )
        self.attachment_creinsa.write(
            {"res_model": invoice._name, "res_id": invoice.id}
        )
        invoice.with_context(
            active_ids=invoice.ids
        ).action_base_import_pdf_by_template_reprocess()
        self._test_account_invoice_creinsa_data(invoice)
        self.assertEqual(len(invoice.attachment_ids), 1)
        # Process again
        self._test_account_invoice_creinsa_data(invoice)
        self.assertEqual(len(invoice.attachment_ids), 1)

    def test_account_invoice_google(self):
        self._set_template_values("account_move_google")
        attachment = self._create_ir_attachment("misc/account-move-google.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "5050834184")
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 19.2)

    def test_account_invoice_ionos(self):
        self._set_template_values("account_move_ionos")
        attachment = self._create_ir_attachment("misc/account-move-ionos.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "202780344094")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 1))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 5)

    def test_account_invoice_ovh(self):
        self._set_template_values("account_move_ovh")
        attachment = self._create_ir_attachment("misc/account-move-ovh.pdf")
        wizard = self._create_wizard_base_import_pdf_upload(attachment)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(attachment, record.attachment_ids)
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "ES3594146")
        self.assertEqual(record.invoice_date, datetime.date(2024, 8, 1))
        self.assertEqual(record.partner_id, self.partner)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 148.57)
