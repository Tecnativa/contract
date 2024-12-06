# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import new_test_user, tagged
from odoo.tests.common import users

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestReimbursementCost(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="analytic.group_analytic_accounting",
        )
        cls.customer_1 = cls.env["res.partner"].create({"name": "Customer 1"})
        cls.default_plan = cls.env["account.analytic.plan"].create({"name": "Default"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "partner_id": cls.customer_1.id,
                "plan_id": cls.default_plan.id,
            }
        )
        cls.bill_1 = cls.init_invoice("in_invoice", amounts=[100])
        cls.bill_1.invoice_line_ids.write(
            {"analytic_distribution": {cls.analytic_account.id: 100}}
        )

    @users("test-user")
    def test_invoice_followers_from_reimbursement(self):
        self.assertNotIn(self.customer_1, self.bill_1.message_partner_ids)
        self.bill_1.is_portal_published = True
        self.assertIn(self.customer_1, self.bill_1.message_partner_ids)
        self.bill_1.is_portal_published = False
        self.assertNotIn(self.customer_1, self.bill_1.message_partner_ids)
        self.analytic_account.partner_id = False
        with self.assertRaisesRegex(
            UserError, "This invoice can't be published to the portal.*"
        ):
            self.bill_1.is_portal_published = True
