import asyncio
from playwright.async_api import async_playwright

from config import START_URL, HEADLESS, create_dirs

from parsers.category_parser import collect_product_links
from parsers.product_parser import parse_product_page

async def main():
    create_dirs()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            channel='chrome',
            args=['-disable-blink-features=AutomationControlled'],
        )
        context = await browser.new_context(
            viewport={"width": 1600, "height": 900},
            locale="uk-UA",
        )

        page = await context.new_page()

        product_links = await collect_product_links(page, START_URL)

        print("\n==============================")
        print(f"Всего найдено товаров: {len(product_links)}")
        print("==============================\n")

        products = []

        for index, url in enumerate(product_links, start=1):
            print(f"[{index}/{len(product_links)}] Парсим: {url}")

            product = await parse_product_page(page, url)
            products.append(product)

        await browser.close()

        print("\nГотово. Собранные товары:")
        print(products)


if __name__ == "__main__":
    asyncio.run(main())