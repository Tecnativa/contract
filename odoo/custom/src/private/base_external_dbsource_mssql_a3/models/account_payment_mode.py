# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentMode(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["account.payment.mode", "dbsource.a3.mixin"]
    _name = "account.payment.mode"
