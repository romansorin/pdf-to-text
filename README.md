# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

pdf-to-text was originally built as an afternoon project to aid a close friend in quickly locating relevant information after receiving several thousands of PDFs in an open records request.

# How it works

Given a source directory containing PDFs,
1. Convert a PDF file into a JPEG using `pdf2image`, exporting all images into a temporary directory;
2. Convert the JPEG into TXT using `pytesseract`, exporting the resulting file text into the output directory;
3. If keywords are provided, scan the text files and check if any keywords are present within the extracted text. If it is, the file is moved to a `matches` directory with the output directory;
4. By default, or if explicitly provided, PDF file sizes will be checked prior to processing. If the file exceeds the max size, the file is moved to a `skipped` within the output directory;
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

- [ ] Allow comma-delimited keywords, phrases
- [ ] Improve/optimize keyword matching (fuzzy/typo checks, keyphrases, trigrams, case-sensitivity, etc.)
- [ ] Add ability to compare dates, filtering
- [ ] Random things like extracting metadata, generate summary, sentiment analysis
- [ ] PDF table to XLSX/CSV table conversion
- [ ] Operating chaining/more flexible API
- [ ] Lite mode/non-GPU req, support for different OCR (?)
- [ ] Indexing of PDFs and content, searching
- [ ] Explore pytesseract options (multi-lang support, timeouts, output more data like confidence for use in more complex workflows)
- [ ] Use temporary directory/temp files for converted PDFs
- [ ] Support runnable command
- [ ] Add tests, mocks/test data
- [ ] Add support for chunks/multiprocessing
- [ ] Remote downloads/uploads