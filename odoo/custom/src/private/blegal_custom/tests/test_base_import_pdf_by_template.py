# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
from base64 import b64encode
from os import path

from odoo.addons.base.tests.common import BaseCommon


class TestBaseImportPdfByTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        # AWS
        cls.partner_aws = cls.env.ref("blegal_custom.res_partner_aws")
        cls.template_aws = cls.env.ref("blegal_custom.account_move_aws")
        cls.template_aws.write(
            {"auto_detect_pattern": r"(?<=console.aws.amazon.com)[\S\s]*"}
        )
        cls.product_aws = cls.env.ref("blegal_custom.product_product_aws")
        product_model_name = cls.product_aws._name
        cls.env.ref("blegal_custom.account_move_aws_line_product_id").write(
            {"default_value": f"{product_model_name},{cls.product_aws.id}"}
        )
        cls.attachment_aws = cls._create_ir_attachment("account-move-aws.pdf")
        # Creinsa
        cls.partner_creinsa = cls.env.ref("blegal_custom.res_partner_creinsa")
        cls.template_creinsa = cls.env.ref("blegal_custom.account_move_creinsa")
        cls.template_creinsa.write({"auto_detect_pattern": r"(?<=creinsa.com)[\S\s]*"})
        cls.product_creinsa = cls.env.ref("blegal_custom.product_product_creinsa")
        product_model_name = cls.product_creinsa._name
        cls.env.ref("blegal_custom.account_move_creinsa_line_product_id").write(
            {"default_value": f"{product_model_name},{cls.product_creinsa.id}"}
        )
        cls.attachment_creinsa = cls._create_ir_attachment("account-move-creinsa.pdf")
        # Google
        cls.partner_google = cls.env.ref("blegal_custom.res_partner_google")
        cls.template_google = cls.env.ref("blegal_custom.account_move_google")
        cls.template_google.write(
            {"auto_detect_pattern": r"(?<=Google Cloud EMEA)[\S\s]*"}
        )
        cls.product_google = cls.env.ref("blegal_custom.product_product_google")
        product_model_name = cls.product_google._name
        cls.env.ref("blegal_custom.account_move_google_line_product_id").write(
            {"default_value": f"{product_model_name},{cls.product_google.id}"}
        )
        cls.attachment_google = cls._create_ir_attachment("account-move-google.pdf")
        # Ionos
        cls.partner_ionos = cls.env.ref("blegal_custom.res_partner_ionos")
        cls.template_ionos = cls.env.ref("blegal_custom.account_move_ionos")
        cls.template_ionos.write({"auto_detect_pattern": r"(?<=IONOS Cloud)[\S\s]*"})
        cls.product_ionos = cls.env.ref("blegal_custom.product_product_ionos")
        product_model_name = cls.product_ionos._name
        cls.env.ref("blegal_custom.account_move_ionos_line_product_id").write(
            {"default_value": f"{product_model_name},{cls.product_ionos.id}"}
        )
        cls.attachment_ionos = cls._create_ir_attachment("account-move-ionos.pdf")
        # OVH
        cls.partner_ovh = cls.env.ref("blegal_custom.res_partner_ovh")
        cls.template_ovh = cls.env.ref("blegal_custom.account_move_ovh")
        cls.template_ovh.write({"auto_detect_pattern": r"(?<=OVH HISPANO S.L)[\S\s]*"})
        cls.product_ovh = cls.env.ref("blegal_custom.product_product_ovh")
        product_model_name = cls.product_ovh._name
        cls.env.ref("blegal_custom.account_move_ovh_line_product_id").write(
            {"default_value": f"{product_model_name},{cls.product_ovh.id}"}
        )
        cls.attachment_ovh = cls._create_ir_attachment("account-move-ovh.pdf")

    @classmethod
    def _data_file(cls, filename):
        file = open(path.join(path.dirname(__file__), "data/" + filename), "rb")
        return b64encode(file.read())

    @classmethod
    def _create_ir_attachment(cls, filename):
        return cls.env["ir.attachment"].create(
            {
                "name": filename,
                "datas": cls._data_file(filename),
            }
        )

    def _create_wizard_base_import_pdf_upload(self, attachment):
        return self.env["wizard.base.import.pdf.upload"].create(
            {
                "model": "account.move",
                "attachment_ids": attachment.ids,
            }
        )

    def _test_account_invoice_aws_data(self, record):
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "EUINES24-84613")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 2))
        self.assertEqual(record.partner_id, self.partner_aws)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product_aws)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 18.34)

    def test_account_invoice_aws_01(self):
        wizard = self._create_wizard_base_import_pdf_upload(self.attachment_aws)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(self.attachment_aws, record.attachment_ids)
        self._test_account_invoice_aws_data(record)

    def test_account_invoice_aws_02(self):
        invoice = self.journal.with_context(
            default_journal_id=self.journal.id
        )._create_document_from_attachment(self.attachment_aws.id)
        self.assertIn(self.attachment_aws, invoice.attachment_ids)
        self._test_account_invoice_aws_data(invoice)

    def _test_account_invoice_creinsa_data(self, record):
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "242164")
        self.assertEqual(record.invoice_date, datetime.date(2024, 8, 1))
        self.assertEqual(record.partner_id, self.partner_creinsa)
        self.assertIn(
            self.product_creinsa, record.mapped("invoice_line_ids.product_id")
        )
        self.assertEqual(len(record.invoice_line_ids), 17)
        self.assertEqual(sum(record.invoice_line_ids.mapped("quantity")), 18)

    def test_account_invoice_creinsa_01(self):
        wizard = self._create_wizard_base_import_pdf_upload(self.attachment_creinsa)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(self.attachment_creinsa, record.attachment_ids)
        self._test_account_invoice_creinsa_data(record)

    def test_account_invoice_creinsa_02(self):
        invoice = self.journal.with_context(
            default_journal_id=self.journal.id
        )._create_document_from_attachment(self.attachment_creinsa.id)
        self.assertIn(self.attachment_creinsa, invoice.attachment_ids)
        self._test_account_invoice_creinsa_data(invoice)

    # def test_account_invoice_google(self):
    #     wizard = self._create_wizard_base_import_pdf_upload(self.attachment_google)
    #     res = wizard.action_process()
    #     self.assertEqual(res["res_model"], "account.move")
    #     record = self.env[res["res_model"]].browse(res["res_id"])
    #     self.assertIn(self.attachment_google, record.attachment_ids)
    #     self.assertEqual(record.move_type, "in_invoice")
    #     self.assertEqual(record.ref, "5050834184")
    #     self.assertEqual(record.partner_id, self.partner_google)
    #     self.assertEqual(len(record.invoice_line_ids), 1)
    #     self.assertEqual(record.invoice_line_ids.product_id, self.product_google)
    #     self.assertEqual(record.invoice_line_ids.quantity, 1)
    #     self.assertEqual(record.invoice_line_ids.price_unit, 19.2)

    def _test_account_invoice_ionos_data(self, record):
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "202780344094")
        self.assertEqual(record.invoice_date, datetime.date(2024, 9, 1))
        self.assertEqual(record.partner_id, self.partner_ionos)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product_ionos)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 5)

    def test_account_invoice_ionos_01(self):
        wizard = self._create_wizard_base_import_pdf_upload(self.attachment_ionos)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(self.attachment_ionos, record.attachment_ids)
        self._test_account_invoice_ionos_data(record)

    def test_account_invoice_ionos_02(self):
        invoice = self.journal.with_context(
            default_journal_id=self.journal.id
        )._create_document_from_attachment(self.attachment_ionos.id)
        self.assertIn(self.attachment_ionos, invoice.attachment_ids)
        self._test_account_invoice_ionos_data(invoice)

    def _test_account_invoice_ovh_data(self, record):
        self.assertEqual(record.move_type, "in_invoice")
        self.assertEqual(record.ref, "ES3594146")
        self.assertEqual(record.invoice_date, datetime.date(2024, 8, 1))
        self.assertEqual(record.partner_id, self.partner_ovh)
        self.assertEqual(len(record.invoice_line_ids), 1)
        self.assertEqual(record.invoice_line_ids.product_id, self.product_ovh)
        self.assertEqual(record.invoice_line_ids.quantity, 1)
        self.assertEqual(record.invoice_line_ids.price_unit, 148.57)

    def test_account_invoice_ovh_01(self):
        wizard = self._create_wizard_base_import_pdf_upload(self.attachment_ovh)
        res = wizard.action_process()
        self.assertEqual(res["res_model"], "account.move")
        record = self.env[res["res_model"]].browse(res["res_id"])
        self.assertIn(self.attachment_ovh, record.attachment_ids)
        self._test_account_invoice_ovh_data(record)

    def test_account_invoice_ovh_02(self):
        invoice = self.journal.with_context(
            default_journal_id=self.journal.id
        )._create_document_from_attachment(self.attachment_ovh.id)
        self.assertIn(self.attachment_ovh, invoice.attachment_ids)
        self._test_account_invoice_ovh_data(invoice)
