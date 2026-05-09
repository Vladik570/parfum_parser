import asyncio

from playwright.async_api import async_playwright

from config import (
    START_URL,
    HEADLESS,
    create_dirs,
)

from parsers.category_parser import collect_product_links
from parsers.product_parser import parse_product_page
from data_storage import (
    save_product_links,
    save_products,
    group_products_by_classification,
    save_grouped_products,
)
from pdf_builder import build_pdf_catalog


async def main() -> None:
    create_dirs()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = await browser.new_context(
            viewport={"width": 1600, "height": 900},
            locale="uk-UA",
        )

        page = await context.new_page()

        product_links = await collect_product_links(page, START_URL)

        save_product_links(product_links)

        print("\n==============================")
        print(f"Total products found: {len(product_links)}")
        print("==============================\n")

        products = []

        for index, url in enumerate(product_links, start=1):
            print(f"[{index}/{len(product_links)}] Parsing: {url}")

            product = await parse_product_page(page, url)
            products.append(product)

        await browser.close()

    save_products(products)

    grouped_products = group_products_by_classification(products)
    save_grouped_products(grouped_products)

    build_pdf_catalog(grouped_products)

    print("\nDone.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupted by user")
