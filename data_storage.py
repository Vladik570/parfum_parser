import json

from config import (
    PRODUCT_LINKS_PATH,
    PRODUCTS_JSON_PATH,
    GROUPED_PRODUCTS_JSON_PATH,
)


VALID_CLASSIFICATIONS = {
    "альдегідні",
    "фужерні",
    "водяні",
    "пряні",
    "східні",
    "гурманські",
    "квіткові",
    "фруктові",
    "цитрусові",
    "деревні",
    "зелені",
    "мускусні",
    "шипрові",
    "шкіряні",
    "пудрові",
    "тютюнові",
    "ароматичні",
    "свіжі",
    "солодкі",
    "ванільні",
    "морські",
    "трав'яні",
    "бальзамічні",
}


def save_product_links(product_links: list[str]) -> None:
    PRODUCT_LINKS_PATH.write_text(
        "\n".join(product_links),
        encoding="utf-8",
    )

    print(f"Product links saved: {PRODUCT_LINKS_PATH}")


def save_products(products: list[dict]) -> None:
    PRODUCTS_JSON_PATH.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Products JSON saved: {PRODUCTS_JSON_PATH}")


def group_products_by_classification(products: list[dict]) -> dict:
    grouped_products = {}

    for product in products:
        classifications = product.get("classifications", [])
        clean_classifications = clean_product_classifications(classifications)

        if not clean_classifications:
            grouped_products.setdefault("без класифікації", []).append(product)
            continue

        product["classifications"] = clean_classifications

        for classification in clean_classifications:
            grouped_products.setdefault(classification, []).append(product)

    return grouped_products


def clean_product_classifications(classifications: list[str]) -> list[str]:
    clean_items = []

    for classification in classifications:
        cleaned = normalize_classification(classification)

        if not cleaned:
            continue

        if cleaned not in VALID_CLASSIFICATIONS:
            continue

        if cleaned not in clean_items:
            clean_items.append(cleaned)

    return clean_items


def normalize_classification(value: str) -> str:
    if not value:
        return ""

    value = str(value).lower()
    value = value.replace("\n", " ")
    value = " ".join(value.split())
    value = value.strip(" .,:;")

    return value


def save_grouped_products(grouped_products: dict) -> None:
    GROUPED_PRODUCTS_JSON_PATH.write_text(
        json.dumps(grouped_products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Grouped products JSON saved: {GROUPED_PRODUCTS_JSON_PATH}")