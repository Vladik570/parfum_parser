from playwright.async_api import Page

from config import (
    MAX_PAGES,
    ELEMENT_WAIT_TIMEOUT,
    PAGE_LOAD_TIMEOUT,
)


async def collect_product_links(page: Page, start_url: str) -> list[str]:
    all_links: list[str] = []
    current_page = 1

    while True:
        if MAX_PAGES is not None and current_page > MAX_PAGES:
            print("Достигнут лимит страниц из config.py")
            break

        url = build_page_url(start_url, current_page)

        print(f"\nОткрываю страницу каталога: {url}")

        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=PAGE_LOAD_TIMEOUT,
        )

        await close_cookie_banner(page)

        await page.wait_for_selector(
            "#products_content",
            timeout=ELEMENT_WAIT_TIMEOUT,
        )

        await page.mouse.wheel(0, 3000)
        await page.wait_for_timeout(1000)

        links = await extract_product_links(page, start_url)

        if not links:
            print("Товары на странице не найдены. Останавливаемся.")
            break

        new_links = []

        for link in links:
            if link not in all_links:
                new_links.append(link)

        if not new_links:
            print("Новых товаров нет. Останавливаемся.")
            break

        all_links.extend(new_links)

        print(f"На странице {current_page} найдено новых товаров: {len(new_links)}")

        current_page += 1

    return all_links


def build_page_url(start_url: str, page_number: int) -> str:
    if page_number == 1:
        return start_url

    return f"{start_url}?page={page_number}"


async def extract_product_links(page: Page, start_url: str) -> list[str]:
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
            .filter(href => !href.includes('checkout'))
            .filter(href => !href.includes('cart'))
        """
    )

    clean_links: list[str] = []

    for link in links:
        if link not in clean_links:
            clean_links.append(link)

    return clean_links


async def close_cookie_banner(page: Page) -> None:
    button = page.get_by_text("Погоджуюся", exact=True)

    try:
        if await button.count() > 0:
            await button.click(timeout=3000)
            await page.wait_for_timeout(500)
    except Exception:
        pass