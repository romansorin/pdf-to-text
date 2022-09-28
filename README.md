# pdf-to-text

Converts batch of PDF to text files, with optional keyword matching to move results into a separate directory. Utilizes Tesseract OCR and pdf2image packages.

## Install

```
python3 -m venv .venv && source .venv/bin/activate
pip install Pillow
pip install -r requirements.txt
mkdir data matches parsed pages skipped
```

## Usage

```
python run_script.py
```
