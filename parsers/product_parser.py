import asyncio
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from config import (
    HTML_DIR,
    IMAGES_DIR,
    SAVE_HTML,
    SAVE_IMAGES,
    PAGE_LOAD_TIMEOUT,
    ELEMENT_WAIT_TIMEOUT,
    DELAY_BETWEEN_PRODUCTS,
)


async def parse_product_page(page: Page, url: str) -> dict:
    try:
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=PAGE_LOAD_TIMEOUT,
        )
    except PlaywrightTimeoutError:
        print(f"Product page loading timeout: {url}")
        return build_empty_product(url)

    try:
        await page.wait_for_selector("h1", timeout=ELEMENT_WAIT_TIMEOUT)
    except PlaywrightTimeoutError:
        print(f"Product title was not found: {url}")

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    filename = make_safe_filename(url)

    html_path = ""
    image_url = ""
    image_path = ""

    if SAVE_HTML:
        html_path = save_html_file(filename, html)

    if SAVE_IMAGES:
        image_url = get_product_image_url(soup)

        if image_url:
            image_path = await download_image(page, image_url, filename)
        else:
            print(f"Product image was not found: {url}")

    product = {
        "name": get_text(soup, "h1"),
        "price": get_product_price(soup),
        "old_price": get_text(soup, ".price-old"),
        "image": image_path,
        "image_url": image_url,
        "url": url,
        "classifications": get_aroma_classifications(soup),
        "html_path": html_path,
    }

    await asyncio.sleep(DELAY_BETWEEN_PRODUCTS)

    return product


def build_empty_product(url: str) -> dict:
    return {
        "name": "",
        "price": "",
        "old_price": "",
        "image": "",
        "image_url": "",
        "url": url,
        "classifications": [],
        "html_path": "",
    }


def save_html_file(filename: str, html: str) -> str:
    html_path = HTML_DIR / f"{filename}.html"
    html_path.write_text(html, encoding="utf-8")
    return str(html_path)


def get_product_image_url(soup: BeautifulSoup) -> str:
    image = soup.select_one(".image img")

    if image and image.get("src"):
        return image["src"]

    image = soup.select_one(".thumbnails img")

    if image and image.get("src"):
        return image["src"]

    image = soup.select_one("img[src*='/files/products/']")

    if image and image.get("src"):
        return image["src"]

    return ""


async def download_image(page: Page, image_url: str, filename: str) -> str:
    try:
        response = await page.context.request.get(image_url)

        if not response.ok:
            print(f"Image download failed: {image_url}")
            return ""

        image_bytes = await response.body()
        extension = get_image_extension(image_url)

        image_path = IMAGES_DIR / f"{filename}{extension}"
        image_path.write_bytes(image_bytes)

        print(f"Image saved: {image_path}")

        return str(image_path)

    except Exception as error:
        print(f"Image download error: {image_url} | {error}")
        return ""


def get_product_price(soup: BeautifulSoup) -> str:
    price = get_text(soup, ".price-new")

    if price:
        return price

    price = get_text(soup, ".price")

    if price:
        match = re.search(r"\d+\s*грн", price)
        if match:
            return match.group(0).replace(" ", "")

    return ""


def get_aroma_classifications(soup: BeautifulSoup) -> list[str]:
    text = soup.get_text(" ", strip=True)

    match = re.search(
        r"Класифікація аромату:\s*(.+?)(?=\s*(Верхня нота:|Середня нота:|Базова нота:|Опис|$))",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return []

    raw_value = match.group(1).strip()

    classifications = []

    for item in raw_value.split(","):
        cleaned = item.strip().lower()

        if cleaned and cleaned not in classifications:
            classifications.append(cleaned)

    return classifications


def get_image_extension(image_url: str) -> str:
    path = urlparse(image_url).path.lower()

    if ".png" in path:
        return ".png"

    if ".webp" in path:
        return ".webp"

    if ".jpeg" in path:
        return ".jpeg"

    return ".jpg"


def get_text(soup: BeautifulSoup, selector: str) -> str:
    element = soup.select_one(selector)

    if not element:
        return ""

    return element.get_text(" ", strip=True)


def make_safe_filename(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug)
    return slug[:150]