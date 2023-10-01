from __future__ import annotations

import argparse
import logging
import os
import shutil

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger()

DIRECTORIES: dict = {
    "input": "data/",
    "output": "output/parsed/",
    "pages": "output/pages/",
    "matches": "output/matches/",
    "skipped": "output/skipped/",
}
DEFAULT_MAX_FILE_SIZE_KB: int = 5120


def get_args():
    # TODO: add additional arguments for progress (tqdm), logging/verbose.
    # add flags to run parsing, matching/searching separately,
    # keep converted files for debug

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-K",
        "--keywords",
        nargs="+",
        default=[],
        help=(
            "A list of keywords to search for in parsed text files. "
            f"Matching files will be moved to the '{DIRECTORIES['matches']}' directory."
        ),
    )
    parser.add_argument(
        "-I",
        "--input-directory",
        type=str,
        default=DIRECTORIES["input"],
        help="The relative directory containing the PDF files to be converted.",
    )
    parser.add_argument(
        "-O",
        "--output-directory",
        type=str,
        default=DIRECTORIES["output"],
        help="The relative directory containing the converted PDF-to-text files.",
    )
    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="If true, reprocesses any PDF files that have already been parsed.",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=DEFAULT_MAX_FILE_SIZE_KB,
        help="Maximum file size to convert to text in KB. Default: 5MB",
    )
    return parser.parse_args()


def process_source(
    source_directory: str = DIRECTORIES["input"],
    max_file_size_kb: int = DEFAULT_MAX_FILE_SIZE_KB,
):
    """Converts all provided PDF files to text and runs the "search_keywords" list
    over these parsed files to match provided keywords."""
    files = []
    matches = 0

    os.makedirs(os.path.dirname(source_directory), exist_ok=True)
    for filename in os.listdir(source_directory):
        if os.path.splitext(filename)[1] == ".pdf":
            print(f"Found PDF: {filename}")
            files.append(filename)

    print(f"Processing files ({len(files)})")
    for filename in files:
        matches = parse_pdf(
            filename, source_directory, matches, max_file_size_kb=max_file_size_kb
        )
    print(f"Finished processing all files. Found {matches} keyword matches")


# TODO: remove, add argument to strictly search over parsed files
def reprocess_output(
    output_directory: str = DIRECTORIES["output"], keywords: list[str] = []
):
    """Runs the "keywords" list over all of the parsed text files to match
    additional keywords following initial pdf to text conversion."""
    files = []
    matches_count = 0

    os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    for filename in os.listdir(output_directory):
        if os.path.splitext(filename)[1] == ".txt":
            print(f"Found file: {filename}")
            files.append(filename)

    print(f"Processing files ({len(files)})")
    for filename in files:
        print(f"Checking file {filename}")
        file = os.path.join(output_directory, filename)
        with open(file, "r") as f:
            text = f.read()
            exists = any(term.lower() in text for term in keywords)
            if exists:
                print(
                    f"Keyword present in file. Moving file to {DIRECTORIES['matches']}"
                )
                matches_count += 1
                os.makedirs(os.path.dirname(DIRECTORIES["matches"]), exist_ok=True)
                shutil.move(file, f"{DIRECTORIES['matches']}/{filename}")

    print(f"Finished processing all files. Found {matches_count} keyword matches")


def parse_pdf(filename, directory, matches, keywords: list[str], max_file_size_kb: int):
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

    outfile = f"{DIRECTORIES['output']}/{base_name}.txt"
    matches_outfile = f"{DIRECTORIES['matches']}/{base_name}.txt"
    skipped_outfile = f"{DIRECTORIES['skipped']}/{base_name}.txt"

    if (
        os.path.exists(matches_outfile)
        or os.path.exists(outfile)
        or os.path.exists(skipped_outfile)
    ):
        print(f"File {filename} has already been parsed, skipping")
        return matches

    # Skip parsing files over the designated file size
    # to prevent timeouts or resource-intensive instances
    if bytesto(filesize) > max_file_size_kb:
        print(f"File {filename} exceeds {max_file_size_kb} limit, skipping")
        os.makedirs(os.path.dirname(DIRECTORIES["skipped"]), exist_ok=True)
        with open(skipped_outfile, "a") as f:
            f.write(f"SKIPPED, byte size {filesize}")
        return matches

    try:
        pages = convert_from_path(path, 500)
    except Exception as exc:
        print(exc)
        return matches
    image_counter = 1

    for page in pages:
        os.makedirs(os.path.dirname(DIRECTORIES["input"]), exist_ok=True)
        filename = get_page_filename(image_counter, base_name)
        print(f"Saving page: {filename}")
        page.save(filename, "JPEG")
        image_counter += 1

    filelimit = image_counter - 1

    os.makedirs(os.path.dirname(DIRECTORIES["output"]), exist_ok=True)
    exists = False
    with open(outfile, "a") as f:
        for i in range(1, filelimit + 1):
            filename = get_page_filename(i, base_name)

            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace("-\n", "")

            exists = any(term.lower() in text for term in keywords)

            f.write(text)

    if exists:
        print(f"Keyword present in file. Moving file to {DIRECTORIES['matches']}")
        matches += 1
        os.makedirs(os.path.dirname(DIRECTORIES["matches"]), exist_ok=True)
        shutil.move(outfile, matches_outfile)

    print(f"Finished writing file: {outfile}")

    for filename in os.listdir(DIRECTORIES["pages"]):
        f = os.path.join(DIRECTORIES["pages"], filename)
        if os.path.isfile(f):
            print(f"Removing file: {DIRECTORIES['pages']}/{filename}")
            os.remove(f)

    print("\n")
    print("-----------")
    print("\n")

    return matches


def get_page_filename(i, base_name):
    return f"{DIRECTORIES['pages']}/{base_name}_page_{str(i)}.jpg"


def bytesto(bytes, to="k", bsize=1024):
    a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
    return bytes / (bsize ** a[to])


def main():
    args = get_args()
    process_source(keywords=args.keywords, max_file_size_kb=args.max_size)
    reprocess_output(
        output_directory=args.output_directory,
        keywords=args.keywords,
    )


if __name__ == "__main__":
    main()
