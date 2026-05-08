from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from config import (
    MAX_PAGES,
    PAGE_LOAD_TIMEOUT,
    ELEMENT_WAIT_TIMEOUT,
)


async def collect_product_links(page: Page, start_url: str) -> list[str]:
    all_links: list[str] = []
    current_page = 1

    while True:
        if MAX_PAGES is not None and current_page > MAX_PAGES:
            print("Page limit reached from config.py")
            break

        catalog_url = build_catalog_page_url(start_url, current_page)

        print(f"\nOpening catalog page: {catalog_url}")

        try:
            await page.goto(
                catalog_url,
                wait_until="domcontentloaded",
                timeout=PAGE_LOAD_TIMEOUT,
            )
        except PlaywrightTimeoutError:
            print(f"Page {current_page} is taking too long to load. Stopping.")
            break

        await close_cookie_banner(page)

        try:
            await page.wait_for_selector(
                "#products_content",
                timeout=ELEMENT_WAIT_TIMEOUT,
            )
        except PlaywrightTimeoutError:
            print(f"Page {current_page} has no product block. Stopping.")
            break

        await page.wait_for_timeout(1000)

        product_links = await get_product_links_from_current_page(page)

        if not product_links:
            print(f"Page {current_page} no products found. End.")
            break

        new_links = []

        for link in product_links:
            if link not in all_links:
                new_links.append(link)

        if not new_links:
            print(f"Page {current_page} no new products found. End.")
            break

        all_links.extend(new_links)

        print(f"Page {current_page}: new products {len(new_links)}")

        current_page += 1

    return all_links


def build_catalog_page_url(start_url: str, page_number: int) -> str:
    if page_number == 1:
        return start_url

    return f"{start_url}?page={page_number}"


async def get_product_links_from_current_page(page: Page) -> list[str]:
    links = await page.locator("#products_content a[href]").evaluate_all(
        """
        elements => elements
            .map(a => a.href)
            .filter(href => href)
            .filter(href => href.includes('parfumcity.com.ua/ua/'))
            .filter(href => !href.includes('/ua/catalog/'))
            .filter(href => !href.includes('page='))
            .filter(href => !href.includes('#'))
            .filter(href => !href.includes('javascript'))
            .filter(href => !href.includes('cart'))
            .filter(href => !href.includes('checkout'))
        """
    )

    unique_links = []

    for link in links:
        if link not in unique_links:
            unique_links.append(link)

    return unique_links


async def close_cookie_banner(page: Page) -> None:
    button = page.get_by_text("Погоджуюся", exact=True)

    try:
        if await button.count() > 0:
            await button.click(timeout=3000)
            await page.wait_for_timeout(500)
    except Exception:
        pass