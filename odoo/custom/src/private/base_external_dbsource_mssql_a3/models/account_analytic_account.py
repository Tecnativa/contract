# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticAccount(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["account.analytic.account", "dbsource.a3.mixin"]
    _name = "account.analytic.account"
