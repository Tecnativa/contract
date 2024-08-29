# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractContract(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["contract.contract", "dbsource.a3.mixin"]
    _name = "contract.contract"


class ContractLine(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["contract.line", "dbsource.a3.mixin"]
    _name = "contract.line"
