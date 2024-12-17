# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["sale.order", "dbsource.a3.mixin"]
    _name = "sale.order"


class SaleOrderLine(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["sale.order.line", "dbsource.a3.mixin"]
    _name = "sale.order.line"
