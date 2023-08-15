# PDF-to-Text

Converts a batch of PDF files to text, with optional keyword matching to move matches into a separate directory using the [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [pdf2image](https://github.com/Belval/pdf2image) packages.

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

## Roadmap

- [] Convert pdf_to_text.py to command, support flags/arguments
- [] Allow flags to be passed to configure quantity, output, keywords, etc.
- [] Add support for subprocesses
- [] Upgrade requirements to latest compatible versions
- [] Remote downloads/uploads
