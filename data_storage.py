import json

from config import (
    PRODUCT_LINKS_PATH,
    PRODUCTS_JSON_PATH,
    GROUPED_PRODUCTS_JSON_PATH,
)


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

        if not classifications:
            grouped_products.setdefault("без класифікації", []).append(product)
            continue

        for classification in classifications:
            grouped_products.setdefault(classification, []).append(product)

    return grouped_products


def save_grouped_products(grouped_products: dict) -> None:
    GROUPED_PRODUCTS_JSON_PATH.write_text(
        json.dumps(grouped_products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Grouped products JSON saved: {GROUPED_PRODUCTS_JSON_PATH}")