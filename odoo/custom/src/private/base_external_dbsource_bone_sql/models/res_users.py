# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResUsers(models.Model):
    """It provides logic for connection to a MySQL data source."""

    _inherit = ["res.users", "dbsource.a3_bone.mixin"]
    _name = "res.users"
