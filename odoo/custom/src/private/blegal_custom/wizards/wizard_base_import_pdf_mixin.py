# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class WizardBaseImportPdfMixin(models.AbstractModel):
    _inherit = "wizard.base.import.pdf.mixin"

    def _pdf_text_extraction_pypdf(self, fileobj):
        """Compatibilidad plantilla FORMAT S.A."""
        res = super()._pdf_text_extraction_pypdf(fileobj)
        for index, item in enumerate(res):
            res[index] = item.replace("\x00", "")
        return res
