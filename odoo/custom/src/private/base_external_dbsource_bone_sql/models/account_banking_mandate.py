# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankingMandate(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["account.banking.mandate", "dbsource.a3_bone.mixin"]
    _name = "account.banking.mandate"
