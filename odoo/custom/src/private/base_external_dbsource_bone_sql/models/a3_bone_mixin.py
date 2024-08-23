# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class A3BoneMixin(models.AbstractModel):
    """It provides the unique key for sqlserver table."""

    _inherit = "dbsource.external.mixin"
    _name = "dbsource.a3_bone.mixin"
    _description = "A3 One Mixin"
    _external_field_key = "a3_key"

    a3_key = fields.Char(copy=False)
