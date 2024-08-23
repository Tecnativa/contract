# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["res.partner", "dbsource.a3.mixin"]
    _name = "res.partner"
    # nexus_mapped_id = fields.One2many(
    #     comodel_name='res.partner.mapped',
    #     inverse_name='partner_id',
    #     readonly=True,
    #     ondelete='restrict'
    # )


class ResPartnerBank(models.Model):
    """It provides logic for connection to a MsSQL data source."""

    _inherit = ["res.partner.bank", "dbsource.a3.mixin"]
    _name = "res.partner.bank"


# class AccountBankingMandate(models.Model):
#     """ It provides logic for connection to a MsSQL data source. """

#     _inherit = ["account.banking.mandate", "dbsource.a3.mixin"]
#     _name = "account.banking.mandate"


# class ResPartnerCategory(models.Model):
#     """ It provides logic for connection to a MsSQL data source. """

#     _inherit = ["res.partner.category", "dbsource.a3.mixin"]
#     _name = "res.partner.category"


class ResPartnerMapped(models.Model):
    """It provides logic for mapped data."""

    _inherit = "dbsource.a3.mixin"
    _name = "res.partner.mapped"

    mapped_key = fields.Char()
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        # ondelete='cascade',
    )
