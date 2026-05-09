PYTHON = python3
PIP = pip

install:
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install

run:
	$(PYTHON) main.py

pdf:
	$(PYTHON) build_pdf_only.py

clean-pdf:
	rm -f output/catalog.pdf

clean-output:
	rm -rf output

freeze:
	$(PIP) freeze > requirements.txt