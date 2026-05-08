from pathlib import Path

# base path
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / 'output'
HTML_DIR = OUTPUT_DIR / 'html'
IMAGES_DIR = OUTPUT_DIR / 'images'

PDF_OUTPUT_PATH = OUTPUT_DIR / 'catalog.pdf'

# start url
START_URL =  "https://parfumcity.com.ua/ua/catalog/frantsuzskie-duhi"

# browser settings
HEADLESS = False

#parse settings
PAGE_LOAD_TIMEOUT = 30000
ELEMENT_WAIT_TIMEOUT = 10000

SAVE_HTML = True
SAVE_IMAGES = True

# None - all pages; 1-16 quality pages
MAX_PAGES = None

# pause between requests
DELAY_BETWEEN_PRODUCTS = 1

def create_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

