from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
HTML_DIR = OUTPUT_DIR / "html"
IMAGES_DIR = OUTPUT_DIR / "images"
DATA_DIR = OUTPUT_DIR / "data"

PRODUCT_LINKS_PATH = DATA_DIR / "product_links.txt"
PRODUCTS_JSON_PATH = DATA_DIR / "products.json"
GROUPED_PRODUCTS_JSON_PATH = DATA_DIR / "grouped_products.json"

PDF_OUTPUT_PATH = OUTPUT_DIR / "catalog.pdf"


START_URL = "https://parfumcity.com.ua/ua/catalog/frantsuzskie-duhi"

HEADLESS = False


PAGE_LOAD_TIMEOUT = 30000
ELEMENT_WAIT_TIMEOUT = 15000

SAVE_HTML = True
SAVE_IMAGES = True

DELAY_BETWEEN_PRODUCTS = 1

MAX_PAGES = 1
# For test: 1 or 2
# For full parsing: None


def create_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)