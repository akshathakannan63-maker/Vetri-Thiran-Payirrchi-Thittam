from datetime import datetime
from pathlib import Path
import re
import unicodedata

from fpdf import FPDF

from config import (
    GENERATED_PDFS_DIR,
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_pdf_text(
    text: str,
) -> str:
    """
    Convert Unicode punctuation into characters
    supported by standard PDF fonts.
    """

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = (
        text
        .encode(
            "latin-1",
            "replace",
        )
        .decode(
            "latin-1"
        )
    )

    return text


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(
    text: str,
) -> str:
    """
    Convert title into a safe filename.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    text = text.strip(
        "_"
    )

    return (
        text[:60]
        or "comiccraft_comic"
    )


# ============================================================
# CREATE PDF
# ============================================================

def create_comic_pdf(
    title: str,
    panels: list,
) -> str:
    """
    Create a PDF containing all comic panels.

    Each panel receives its own page.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{safe_filename(title)}_"
        f"{timestamp}.pdf"
    )

    output_path = (
        GENERATED_PDFS_DIR
        / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in panels:

        pdf.add_page()

        # ----------------------------------------------------
        # PANEL TITLE
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            20,
        )

        panel_title = (
            f"Panel "
            f"{panel['panel_number']}: "
            f"{panel['title']}"
        )

        pdf.multi_cell(
            0,
            10,
            clean_pdf_text(
                panel_title
            ),
        )

        pdf.ln(3)

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=15,
                y=40,
                w=180,
            )

        # Leave room for image

        pdf.set_y(145)

        # ----------------------------------------------------
        # SCENE DESCRIPTION
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            clean_pdf_text(
                panel[
                    "scene_description"
                ]
            ),
        )

        pdf.ln(3)

        # ----------------------------------------------------
        # CAPTION
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.cell(
            0,
            7,
            "Caption",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            clean_pdf_text(
                panel[
                    "caption"
                ]
            ),
        )

        pdf.ln(2)

        # ----------------------------------------------------
        # NARRATION
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.cell(
            0,
            7,
            "Narration",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            clean_pdf_text(
                panel[
                    "narration"
                ]
            ),
        )

        # ----------------------------------------------------
        # DIALOGUE
        # ----------------------------------------------------

        dialogue = (
            panel.get(
                "dialogue",
                "",
            )
            or ""
        ).strip()

        if dialogue:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.cell(
                0,
                7,
                "Dialogue",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                clean_pdf_text(
                    dialogue
                ),
            )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    pdf.output(
        str(output_path)
    )

    return str(
        output_path
    )