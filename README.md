# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

pdf-to-text was originally built as an afternoon project to aid a close friend in quickly locating relevant information after receiving several thousands of PDFs in an open records request.

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

- [] Convert pdf_to_text.py to command, support flags/arguments
- [] Allow flags to be passed to configure quantity, output, keywords, etc.
- [] Add support for subprocesses
- [] Upgrade requirements to latest compatible versions
- [] Remote downloads/uploads
- [] Add tests, mocks/test data
- [] Linting/formatting rules
