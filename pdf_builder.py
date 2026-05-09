from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from config import PDF_OUTPUT_PATH, PRODUCTS_PER_PAGE


FONT_REGULAR_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FONT_REGULAR_NAME = "DejaVuSans"
FONT_BOLD_NAME = "DejaVuSans-Bold"


PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_LEFT = 14 * mm
MARGIN_RIGHT = 14 * mm
MARGIN_TOP = 14 * mm
MARGIN_BOTTOM = 14 * mm

CARD_GAP = 4 * mm
CARD_HEIGHT = 36 * mm

IMAGE_SIZE = 28 * mm

CHECKBOX_SIZE = 4.5 * mm


def build_pdf_catalog(grouped_products: dict) -> None:
    register_fonts()

    pdf = canvas.Canvas(str(PDF_OUTPUT_PATH), pagesize=A4)

    page_number = 1
    product_index = 1

    current_y = PAGE_HEIGHT - MARGIN_TOP

    draw_catalog_title(pdf, page_number)
    current_y -= 18 * mm

    for classification, products in grouped_products.items():
        current_y = ensure_space_for_header(pdf, current_y, page_number)
        draw_classification_header(pdf, classification, current_y)
        current_y -= 10 * mm

        products_on_current_page = 0

        for product in products:
            if products_on_current_page >= PRODUCTS_PER_PAGE:
                draw_footer(pdf, page_number)
                pdf.showPage()
                page_number += 1

                draw_catalog_title(pdf, page_number)
                current_y = PAGE_HEIGHT - MARGIN_TOP - 18 * mm

                draw_classification_header(pdf, classification, current_y)
                current_y -= 10 * mm

                products_on_current_page = 0

            if current_y - CARD_HEIGHT < MARGIN_BOTTOM:
                draw_footer(pdf, page_number)
                pdf.showPage()
                page_number += 1

                draw_catalog_title(pdf, page_number)
                current_y = PAGE_HEIGHT - MARGIN_TOP - 18 * mm

                draw_classification_header(pdf, classification, current_y)
                current_y -= 10 * mm

                products_on_current_page = 0

            draw_product_card(
                pdf=pdf,
                product=product,
                x=MARGIN_LEFT,
                y_top=current_y,
                width=PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT,
                height=CARD_HEIGHT,
                product_index=product_index,
            )

            current_y -= CARD_HEIGHT + CARD_GAP
            product_index += 1
            products_on_current_page += 1

        if current_y - CARD_HEIGHT < MARGIN_BOTTOM:
            draw_footer(pdf, page_number)
            pdf.showPage()
            page_number += 1
            draw_catalog_title(pdf, page_number)
            current_y = PAGE_HEIGHT - MARGIN_TOP - 18 * mm

    draw_footer(pdf, page_number)
    pdf.save()

    print(f"PDF catalog saved: {PDF_OUTPUT_PATH}")


def draw_catalog_title(pdf: canvas.Canvas, page_number: int) -> None:
    pdf.setFont(FONT_BOLD_NAME, 16)
    pdf.setFillColor(colors.black)

    title = "Каталог парфумів"
    title_width = pdfmetrics.stringWidth(title, FONT_BOLD_NAME, 16)

    pdf.drawString(
        (PAGE_WIDTH - title_width) / 2,
        PAGE_HEIGHT - MARGIN_TOP,
        title,
    )


def draw_classification_header(
    pdf: canvas.Canvas,
    classification: str,
    y: float,
) -> None:
    text = f"Класифікація: {clean_text(classification, 80)}"

    pdf.setFont(FONT_BOLD_NAME, 11)
    pdf.setFillColor(colors.black)
    pdf.drawString(MARGIN_LEFT, y, text)


def ensure_space_for_header(
    pdf: canvas.Canvas,
    current_y: float,
    page_number: int,
) -> float:
    if current_y - 20 * mm < MARGIN_BOTTOM:
        draw_footer(pdf, page_number)
        pdf.showPage()
        draw_catalog_title(pdf, page_number + 1)
        return PAGE_HEIGHT - MARGIN_TOP - 18 * mm

    return current_y


def draw_product_card(
    pdf: canvas.Canvas,
    product: dict,
    x: float,
    y_top: float,
    width: float,
    height: float,
    product_index: int,
) -> None:
    y_bottom = y_top - height

    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(0.6)
    pdf.rect(x, y_bottom, width, height)

    checkbox_x = x + 4 * mm
    checkbox_y_top = y_top - 8 * mm

    draw_interactive_checkboxes(
        pdf=pdf,
        x=checkbox_x,
        y=checkbox_y_top,
        product_index=product_index,
    )

    image_x = x + 28 * mm
    image_y = y_bottom + 4 * mm

    draw_product_image(
        pdf=pdf,
        image_path=product.get("image", ""),
        x=image_x,
        y=image_y,
    )

    text_x = image_x + IMAGE_SIZE + 8 * mm
    text_y = y_top - 8 * mm

    text_width = x + width - text_x - 6 * mm

    name = clean_text(product.get("name", ""), 150)
    price = clean_text(product.get("price", ""), 40)
    classifications = clean_text(", ".join(product.get("classifications", [])), 100)
    url = product.get("url", "")

    pdf.setFillColor(colors.black)

    text_y = draw_wrapped_text(
        pdf=pdf,
        label="Назва:",
        value=name,
        x=text_x,
        y=text_y,
        max_width=text_width,
        max_lines=2,
    )

    text_y -= 2 * mm

    text_y = draw_wrapped_text(
        pdf=pdf,
        label="Ціна:",
        value=price,
        x=text_x,
        y=text_y,
        max_width=text_width,
        max_lines=1,
    )

    text_y -= 2 * mm

    text_y = draw_wrapped_text(
        pdf=pdf,
        label="Класифікація:",
        value=classifications,
        x=text_x,
        y=text_y,
        max_width=text_width,
        max_lines=2,
    )

    text_y -= 2 * mm

    draw_product_link(
        pdf=pdf,
        url=url,
        x=text_x,
        y=text_y,
    )


def draw_interactive_checkboxes(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    product_index: int,
) -> None:
    pdf.setFont(FONT_BOLD_NAME, 8)
    pdf.setFillColor(colors.black)

    ok_name = f"ok_{product_index}"
    reject_name = f"reject_{product_index}"

    pdf.acroForm.checkbox(
        name=ok_name,
        tooltip="Approved",
        x=x,
        y=y,
        size=CHECKBOX_SIZE,
        buttonStyle="check",
        borderStyle="solid",
        borderWidth=1,
        borderColor=colors.black,
        fillColor=colors.white,
        textColor=colors.green,
        forceBorder=True,
    )

    pdf.drawString(x + CHECKBOX_SIZE + 2 * mm, y + 1 * mm, "✓")

    second_y = y - 7 * mm

    pdf.acroForm.checkbox(
        name=reject_name,
        tooltip="Rejected",
        x=x,
        y=second_y,
        size=CHECKBOX_SIZE,
        buttonStyle="cross",
        borderStyle="solid",
        borderWidth=1,
        borderColor=colors.black,
        fillColor=colors.white,
        textColor=colors.red,
        forceBorder=True,
    )

    pdf.drawString(x + CHECKBOX_SIZE + 2 * mm, second_y + 1 * mm, "✗")


def draw_product_image(
    pdf: canvas.Canvas,
    image_path: str,
    x: float,
    y: float,
) -> None:
    if not image_path:
        return

    path = Path(image_path)

    if not path.exists():
        return

    try:
        image = ImageReader(str(path))

        pdf.drawImage(
            image,
            x,
            y,
            width=IMAGE_SIZE,
            height=IMAGE_SIZE,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

    except Exception:
        return


def draw_product_link(
    pdf: canvas.Canvas,
    url: str,
    x: float,
    y: float,
) -> None:
    if not url:
        return

    link_text = "Відкрити товар"

    pdf.setFont(FONT_REGULAR_NAME, 8)
    pdf.setFillColor(colors.blue)
    pdf.drawString(x, y, link_text)

    link_width = pdfmetrics.stringWidth(link_text, FONT_REGULAR_NAME, 8)

    pdf.linkURL(
        url,
        rect=(x, y - 1 * mm, x + link_width, y + 4 * mm),
        relative=0,
    )

    pdf.setFillColor(colors.black)


def draw_wrapped_text(
    pdf: canvas.Canvas,
    label: str,
    value: str,
    x: float,
    y: float,
    max_width: float,
    max_lines: int,
) -> float:
    label_text = f"{label} "
    full_text = f"{label_text}{value}"

    lines = wrap_text(
        text=full_text,
        font_name=FONT_REGULAR_NAME,
        font_size=8,
        max_width=max_width,
        max_lines=max_lines,
    )

    for line in lines:
        pdf.setFont(FONT_REGULAR_NAME, 8)
        pdf.setFillColor(colors.black)
        pdf.drawString(x, y, line)
        y -= 4 * mm

    return y


def wrap_text(
    text: str,
    font_name: str,
    font_size: int,
    max_width: float,
    max_lines: int,
) -> list[str]:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = word if not current_line else f"{current_line} {word}"
        test_width = pdfmetrics.stringWidth(test_line, font_name, font_size)

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)

            current_line = word

            if len(lines) >= max_lines:
                break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]

    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = lines[-1].rstrip(".") + "..."

    return lines


def draw_footer(pdf: canvas.Canvas, page_number: int) -> None:
    pdf.setFont(FONT_REGULAR_NAME, 7)
    pdf.setFillColor(colors.grey)

    footer_text = f"Page {page_number}"
    pdf.drawRightString(
        PAGE_WIDTH - MARGIN_RIGHT,
        MARGIN_BOTTOM / 2,
        footer_text,
    )


def clean_text(value: str, max_length: int) -> str:
    if value is None:
        return ""

    value = str(value)
    value = " ".join(value.split())

    if len(value) > max_length:
        value = value[:max_length].rstrip() + "..."

    return value


def register_fonts() -> None:
    if not Path(FONT_REGULAR_PATH).exists():
        raise FileNotFoundError(f"Font was not found: {FONT_REGULAR_PATH}")

    if not Path(FONT_BOLD_PATH).exists():
        raise FileNotFoundError(f"Font was not found: {FONT_BOLD_PATH}")

    pdfmetrics.registerFont(TTFont(FONT_REGULAR_NAME, FONT_REGULAR_PATH))
    pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, FONT_BOLD_PATH))