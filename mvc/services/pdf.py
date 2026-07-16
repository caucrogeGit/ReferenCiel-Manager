# pyright: strict
"""Rendu PDF générique (ADR-024).

Une seule responsabilité : transformer un document HTML complet en octets PDF,
via WeasyPrint. Aucune connaissance du métier — l'appelant fournit le HTML (rendu
depuis un template Jinja).

C'est la COUTURE D'EXTRACTION vers un futur opt-in `forge-mvc-pdf` : ce module est
destiné à migrer tel quel dans le paquet Forge, l'application ne gardant que la
construction du contenu (cf. mvc/services/scenario_pdf.py).
"""
from typing import Any, cast

from weasyprint import HTML  # pyright: ignore[reportMissingTypeStubs]


def render_pdf(html: str, base_url: "str | None" = None) -> bytes:
    """Rend un document HTML complet en octets PDF.

    `base_url` sert à résoudre les chemins relatifs (images, feuilles de style) ;
    laissé à None quand le HTML est autosuffisant (styles en ligne).
    """
    document: Any = HTML(string=html, base_url=base_url)
    return cast(bytes, document.write_pdf())
