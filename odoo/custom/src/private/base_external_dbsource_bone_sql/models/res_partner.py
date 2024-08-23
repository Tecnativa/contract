# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["res.partner", "dbsource.a3_bone.mixin"]
    _name = "res.partner"


class ResPartnerBank(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["res.partner.bank", "dbsource.a3_bone.mixin"]
    _name = "res.partner.bank"


class ResPartnerMapped(models.Model):
    """It provides logic for mapped data."""

    _inherit = "dbsource.a3_bone.mixin"
    _name = "res.partner.mapped"
    _description = "Partner Mapped"

    mapped_key = fields.Char()
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        # ondelete='cascade',
    )
