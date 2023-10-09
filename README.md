# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

pdf-to-text was originally built as an afternoon project to aid a close friend in quickly locating relevant information after receiving several thousands of PDFs in an open records request.

# How it works

PDF-to-Text works by:

Given a source directory containing PDFs,
  - Convert the PDF file into a JPEG using pdf2image, placing all pdf -> JPEG conversions into the `PAGES` directory
  - Extract all text from the JPEG using pytesseract, placing the extracted text into the `PARSED` directory
  - Given a list of search or match keywords, check if any of these keywords are present within the extracted text; if a keyword is present, move the text file to the `MATCHES` directory
  - If a MAX_FILE size is provided, any PDFs that exceed this size will be moved to the `SKIPPED` directory for later processing
  - Any source PDFs remaining in the `PAGES` directory (i.e., not skipped) are then deleted

## Installation

Usage of this package requires [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) as well as package dependencies:

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

After installing dependencies, you can run the `pdf_to_text` command with the `-h` flag to see all available options:

```sh
python src/pdf_to_text.py -h
```


### Local Development

A separate `requirements-dev.txt` file is included for linting, pre-commit checks, testing, etc. To start, create a virtualenv and install all dependencies:

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Roadmap/TODO

- [ ] Improve keyword matching (e.g., fuzzy/typo checks)
- [ ] Add support for chunks/multiprocessing
- [ ] Remote downloads/uploads
- [ ] Add tests, mocks/test data
- [ ] Clean up fn arguments, directory references