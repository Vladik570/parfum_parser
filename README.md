# parfume_parser

Парсер parfumcity + генерация PDF-каталога.

## Требования

- Python 3.9+
- GNU Make
- Интернет для установки зависимостей и Playwright-браузера

## Быстрый старт

Установка (создаст `.venv`, поставит зависимости и скачает Chromium для Playwright):

```bash
make install
```

Запуск парсинга:

```bash
make run
```

Сборка PDF из уже сохранённого `output/data/products.json`:

```bash
make pdf
```

## Полезные команды

- `make clean-pdf` — удалить `output/catalog.pdf`
- `make clean-output` — удалить всю папку `output/`
- `make freeze` — обновить `requirements.txt` из виртуального окружения

## Если что-то не запускается

- Linux: для `python -m venv` может понадобиться пакет `python3-venv` (название зависит от дистрибутива).
- Linux: Playwright может потребовать системные библиотеки для запуска Chromium (зависит от дистрибутива/окружения).
- PDF/шрифты: если не находятся TTF-шрифты, задай пути явно:
  - `CATALOG_FONT_REGULAR` — путь к regular `.ttf`
  - `CATALOG_FONT_BOLD` — путь к bold `.ttf`
