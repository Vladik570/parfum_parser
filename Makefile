.PHONY: help venv install run pdf only-pdf clean-pdf clean-output freeze

VENV_DIR := .venv

ifeq ($(OS),Windows_NT)
	SYS_PY ?= py -3
	VENV_PY := $(VENV_DIR)/Scripts/python.exe
else
	SYS_PY ?= python3
	VENV_PY := $(VENV_DIR)/bin/python
endif

help:
	@echo "Targets:"
	@echo "  make install      Create venv + install deps + playwright browsers"
	@echo "  make run          Run parser (main.py)"
	@echo "  make pdf          Build PDF from existing products.json (only_pdf_builder.py)"
	@echo "  make clean-pdf    Delete output/catalog.pdf"
	@echo "  make clean-output Delete output/ directory"
	@echo "  make freeze       Update requirements.txt from venv"

$(VENV_PY):
	$(SYS_PY) -m venv $(VENV_DIR)
	"$(VENV_PY)" -m pip install --upgrade pip

venv: $(VENV_PY)

install: $(VENV_PY)
	"$(VENV_PY)" -m pip install -r requirements.txt
	"$(VENV_PY)" -m playwright install chromium

run: $(VENV_PY)
	"$(VENV_PY)" main.py

pdf:
	@$(MAKE) only-pdf

only-pdf: $(VENV_PY)
	"$(VENV_PY)" only_pdf_builder.py

clean-pdf:
	$(SYS_PY) -c "from pathlib import Path; Path('output/catalog.pdf').unlink(missing_ok=True)"

clean-output:
	$(SYS_PY) -c "import shutil; shutil.rmtree('output', ignore_errors=True)"

freeze: $(VENV_PY)
	"$(VENV_PY)" -m pip freeze > requirements.txt
