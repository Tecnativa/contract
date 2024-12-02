# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64encode
from os import path

from odoo.addons.base.tests.common import BaseCommon


class TestBaseImportPdfByTemplateBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        plan = cls.env["account.analytic.plan"].create({"name": "Test plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test account",
                "plan_id": plan.id,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )

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

    @classmethod
    def _set_template_values(cls, xml_id):
        template = cls.env.ref(f"blegal_custom.{xml_id}")
        template.line_ids.filtered(
            lambda x: x.field_id.name == "partner_id"
        ).fixed_value = f"res.partner,{cls.partner.id}"
        template.line_ids.filtered(
            lambda x: x.field_id.name == "product_id"
        ).default_value = f"product.product,{cls.product.id}"
        template.line_ids.filtered(
            lambda x: x.field_id.name == "analytic_distribution"
        ).fixed_value_text = '{"%s": 100.0}' % (cls.analytic_account.id)

    def _create_wizard_base_import_pdf_upload(self, attachment):
        return self.env["wizard.base.import.pdf.upload"].create(
            {
                "model": "account.move",
                "attachment_ids": attachment.ids,
            }
        )
