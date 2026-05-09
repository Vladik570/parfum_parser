import json

from config import PRODUCTS_JSON_PATH
from data_storage import (
    group_products_by_classification,
    save_grouped_products,
)
from pdf_builder import build_pdf_catalog


def main() -> None:
    products = json.loads(
        PRODUCTS_JSON_PATH.read_text(encoding="utf-8")
    )

    grouped_products = group_products_by_classification(products)

    save_grouped_products(grouped_products)

    build_pdf_catalog(grouped_products)


if __name__ == "__main__":
    main()