import os
import shutil

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Define directories
PARSED_DIRECTORY = "parsed"
PAGES_DIRECTORY = "pages"
SOURCE_DIRECTORY = "data"
MATCHES_DIRECTORY = "matches"
SKIPPED_DIRECTORY = "skipped"
MAX_FILE_MB_SIZE = 3.0

# Define keywords to do an initial and second-pass search for
extraneous_keywords = []
search_keywords = [] + extraneous_keywords


def process_source():
    """Converts all provided PDF files to text and runs the "search_keywords" list
    over these parsed files to match provided keywords."""
    files = []
    matches = 0

    for filename in os.listdir(SOURCE_DIRECTORY):
        if os.path.splitext(filename)[1] == ".pdf":
            print(f"Found PDF: {filename}")
            files.append(filename)

    print(f"Processing files ({len(files)})")
    for filename in files:
        matches = parse_pdf(filename, SOURCE_DIRECTORY, matches)
    print(f"Finished processing all files. Found {matches} keyword matches")


def reprocess_output():
    """Runs the "extraneous_keywords" list over all of the parsed text files to match
    additional keywords following initial pdf to text conversion."""
    files = []
    matches = 0

    for filename in os.listdir(PARSED_DIRECTORY):
        if os.path.splitext(filename)[1] == ".txt":
            print(f"Found file: {filename}")
            files.append(filename)

    print(f"Processing files ({len(files)})")
    for filename in files:
        print(f"Checking file {filename}")
        file = os.path.join(PARSED_DIRECTORY, filename)
        with open(file, "r") as f:
            text = f.read()
            exists = any(term.lower() in text for term in extraneous_keywords)
            if exists:
                print(f"Keyword present in file. Moving file to {MATCHES_DIRECTORY}")
                matches += 1
                shutil.move(file, f"{MATCHES_DIRECTORY}/{filename}")

    print(f"Finished processing all files. Found {matches} keyword matches")


def parse_pdf(filename, directory, matches):
    """Converts a PDF file into a text file.

    Args:
        filename (str): The name of the PDF
        directory (str): The directory where the PDF is found
        matches (int): A count of files that have been matched against keywords

    Returns:
        [int]: A count of files that have been matched against keywords
    """
    print(f"Beginning file parsing: {filename}")
    path = f"{directory}/{filename}"
    filesize = os.path.getsize(path)
    (base_name, ext) = os.path.splitext(filename)

    outfile = f"{PARSED_DIRECTORY}/{base_name}.txt"
    matches_outfile = f"{MATCHES_DIRECTORY}/{base_name}.txt"
    skipped_outfile = f"{SKIPPED_DIRECTORY}/{base_name}.txt"

    if (
        os.path.exists(matches_outfile)
        or os.path.exists(outfile)
        or os.path.exists(skipped_outfile)
    ):
        print(f"File {filename} has already been parsed, skipping")
        return matches

    # Skip parsing files over the designated file size
    # to prevent timeouts or resource-intensive instances
    if bytesto(filesize, "m") > MAX_FILE_MB_SIZE:
        print(f"File {filename} exceeds 3mb limit, skipping")
        f = open(skipped_outfile, "a")
        f.write(f"SKIPPED, byte size {filesize}")
        f.close()
        return matches

    try:
        pages = convert_from_path(path, 500)
    except Exception as exc:
        print(exc)
        return matches
    image_counter = 1

    for page in pages:
        filename = get_page_filename(image_counter, base_name)
        print(f"Saving page: {filename}")
        page.save(filename, "JPEG")
        image_counter += 1

    filelimit = image_counter - 1

    f = open(outfile, "a")
    exists = False

    for i in range(1, filelimit + 1):
        filename = get_page_filename(i, base_name)

        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        text = text.replace("-\n", "")

        exists = any(term.lower() in text for term in search_keywords)

        f.write(text)

    f.close()

    if exists:
        print(f"Keyword present in file. Moving file to {MATCHES_DIRECTORY}")
        matches += 1
        shutil.move(outfile, matches_outfile)

    print(f"Finished writing file: {outfile}")

    for filename in os.listdir(PAGES_DIRECTORY):
        f = os.path.join(PAGES_DIRECTORY, filename)
        if os.path.isfile(f):
            print(f"Removing file: {PAGES_DIRECTORY}/{filename}")
            os.remove(f)

    print("\n")
    print("-----------")
    print("\n")

    return matches


def get_page_filename(i, base_name):
    return f"{PAGES_DIRECTORY}/{base_name}_page_{str(i)}.jpg"


def bytesto(bytes, to, bsize=1024):
    a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
    return bytes / (bsize ** a[to])


def main():
    process_source()
    reprocess_output()


if __name__ == "__main__":
    main()
