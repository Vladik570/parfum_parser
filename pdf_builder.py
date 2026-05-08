from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
)

from config import PDF_OUTPUT_PATH


FONT_REGULAR_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FONT_REGULAR_NAME = "DejaVuSans"
FONT_BOLD_NAME = "DejaVuSans-Bold"


def build_pdf_catalog(grouped_products: dict) -> None:
    register_fonts()

    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CatalogTitle",
        parent=styles["Title"],
        fontName=FONT_BOLD_NAME,
        fontSize=18,
        leading=22,
        spaceAfter=8,
    )

    group_style = ParagraphStyle(
        "GroupTitle",
        parent=styles["Heading2"],
        fontName=FONT_BOLD_NAME,
        fontSize=14,
        leading=18,
        spaceBefore=10,
        spaceAfter=8,
    )

    header_style = ParagraphStyle(
        "HeaderText",
        parent=styles["Normal"],
        fontName=FONT_BOLD_NAME,
        fontSize=8,
        leading=10,
    )

    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontName=FONT_REGULAR_NAME,
        fontSize=8,
        leading=10,
    )

    story = []

    story.append(Paragraph("Каталог парфумів", title_style))
    story.append(Spacer(1, 6 * mm))

    for classification, products in grouped_products.items():
        story.append(Paragraph(f"Класифікація: {classification}", group_style))

        table_data = [
            [
                Paragraph("Фото", header_style),
                Paragraph("Назва", header_style),
                Paragraph("Ціна", header_style),
                Paragraph("Класифікація", header_style),
                Paragraph("URL", header_style),
            ]
        ]

        for product in products:
            image_cell = build_image_cell(product.get("image", ""))

            name = product.get("name", "")
            price = product.get("price", "")
            url = product.get("url", "")
            classifications = ", ".join(product.get("classifications", []))

            table_data.append(
                [
                    image_cell,
                    Paragraph(name, cell_style),
                    Paragraph(price, cell_style),
                    Paragraph(classifications, cell_style),
                    Paragraph(url, cell_style),
                ]
            )

        table = Table(
            table_data,
            colWidths=[30 * mm, 75 * mm, 25 * mm, 45 * mm, 100 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),

                    ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD_NAME),
                    ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR_NAME),

                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(table)
        story.append(PageBreak())

    doc.build(story)

    print(f"PDF catalog saved: {PDF_OUTPUT_PATH}")


def register_fonts() -> None:
    if not Path(FONT_REGULAR_PATH).exists():
        raise FileNotFoundError(f"Font was not found: {FONT_REGULAR_PATH}")

    if not Path(FONT_BOLD_PATH).exists():
        raise FileNotFoundError(f"Font was not found: {FONT_BOLD_PATH}")

    pdfmetrics.registerFont(TTFont(FONT_REGULAR_NAME, FONT_REGULAR_PATH))
    pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, FONT_BOLD_PATH))


def build_image_cell(image_path: str):
    if not image_path:
        return ""

    path = Path(image_path)

    if not path.exists():
        return ""

    try:
        return Image(str(path), width=25 * mm, height=25 * mm)
    except Exception:
        return ""