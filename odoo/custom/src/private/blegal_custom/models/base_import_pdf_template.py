# Copyright 2024-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class BaseImportPdfTemplateLine(models.Model):
    _inherit = "base.import.pdf.template.line"

    def _process_datetime_value(self, value):
        """Compatibilidad plantilla Movistar."""
        value = value.replace(" de ", " ")
        month_names_mapped = {
            "Enero": "January",
            "Febrero": "February",
            "Marzo": "March",
            "Abril": "April",
            "Mayo": "May",
            "Junio": "June",
            "Julio": "July",
            "Agosto": "August",
            "Septiembre": "September",
            "Octubre": "Octuber",
            "Noviembre": "November",
            "Diciembre": "December",
        }
        for key in list(month_names_mapped.keys()):
            value = value.replace(key, month_names_mapped[key])
            value = value.replace(key.lower(), month_names_mapped[key])
            # Compatibilidad manuel robles
            short_es = key[:3].lower()
            short_en = month_names_mapped[key][:3].lower()
            value = value.replace("-%s-" % short_es, "-%s-" % short_en)
        value = value.replace("sept ", "sep ")  # Custom google_ads
        return super()._process_datetime_value(value)
