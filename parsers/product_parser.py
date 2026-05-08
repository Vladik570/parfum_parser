import asyncio
from pathlib import Path

from bs4 import BeautifulSoup

from config import (
    HTML_DIR,
    SAVE_HTML,
    ELEMENT_WAIT_TIMEOUT,
    DELAY_BETWEEN_PRODUCTS,
)


async def parse_product_page(page, url: str) -> dict:
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_selector("h1", timeout=ELEMENT_WAIT_TIMEOUT)

    html = await page.content()

    if SAVE_HTML:
        filename = make_safe_filename(url)
        html_path = HTML_DIR / f"{filename}.html"
        html_path.write_text(html, encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")

    title = get_text(soup, "h1")
    price = get_text(soup, ".price, .product-price, .price-new")
    old_price = get_text(soup, ".price-old")
    description = get_text(soup, "#tab-description, .tab-description, .description")

    await asyncio.sleep(DELAY_BETWEEN_PRODUCTS)

    return {
        "url": url,
        "title": title,
        "price": price,
        "old_price": old_price,
        "description": description,
    }


def get_text(soup: BeautifulSoup, selector: str) -> str:
    element = soup.select_one(selector)

    if not element:
        return ""

    return element.get_text(strip=True)


def make_safe_filename(url: str) -> str:
    return url.rstrip("/").split("/")[-1]