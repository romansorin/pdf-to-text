# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

pdf-to-text was originally built as an afternoon project to aid a close friend in quickly locating relevant information after receiving several thousands of PDFs in an open records request.

# How it works

Given a source directory containing PDFs,
1. Convert a PDF file into a JPEG using `pdf2image`, exporting all images into the `output/pages` directory;
2. Convert the JPEG into TXT using `pytesseract`, exporting the resulting file text into the `output/parsed` directory;
3. If keywords are provided, scan the text files and check if any keywords are present within the extracted text. If it is, the file is moved to the `output/matches` directory;
4. By default, or if explicitly provided, PDF file sizes will be checked prior to processing. If the file exceeds the max size, the file is moved to the `output/skipped` directory;
5. Unless explicitly specified, all images converted from PDF are deleted after the PDF processing stage.

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

- [ ] Clean up fn arguments, directory references
- [ ] Improve keyword matching (e.g., fuzzy/typo checks)
- [ ] Support runnable command
- [ ] Add tests, mocks/test data
- [ ] Add support for chunks/multiprocessing
- [ ] Remote downloads/uploads