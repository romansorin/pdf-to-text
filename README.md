# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

pdf-to-text was originally built as an afternoon project to aid a close friend in quickly locating relevant information after receiving several thousands of PDFs in an open records request.

# How pdf2t works

PDF-to-Text (`pdf2t`) works by:

Given a source directory containing PDFs,
  - Convert the PDF file into a JPEG using pdf2image, placing all pdf -> JPEG conversions into the `PAGES` directory
  - Extract all text from the JPEG using pytesseract, placing the extracted text into the `PARSED` directory
  - Given a list of search or match keywords, check if any of these keywords are present within the extracted text; if a keyword is present, move the text file to the `MATCHES` directory
  - If a MAX_FILE size is provided, any PDFs that exceed this size will be moved to the `SKIPPED` directory for later processing
  - Any source PDFs remaining in the `PAGES` directory (i.e., not skipped) are then deleted

## Installation

Docker is used to build and run pdf-to-text. To install, verify that you have [Docker](https://www.docker.com) installed, and build the image:

```sh
docker build -t pdf-to-text .
```

## Usage

After building, run the image with any necessary flags provided:

```sh
docker run pdf-to-text --flags
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update and add tests as appropriate.

### Local Development

A separate `requirements-dev.txt` file is included for linting, pre-commit checks, testing, etc. To start, create a virtualenv and install all dependencies:

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Roadmap

- [ ] General cleanup, split out multiple operations into separate functions
- [ ] Convert pdf_to_text.py to command, support flags/arguments to configure behavior
- [ ] Allow flags to be passed to configure file size limits, output, keywords, etc.
- [ ] Improve keyword matching, determine why/if re-processing is necessary
- [ ] Add support for subprocesses
- [ ] Remote downloads/uploads
- [ ] Add typing
- [ ] Add tests, mocks/test data
