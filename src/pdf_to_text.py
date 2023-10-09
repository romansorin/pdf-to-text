from __future__ import annotations

import argparse
import logging
import os
import shutil
from typing import Union

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger("pdf_to_text")


DIRECTORIES: dict[str, str] = {
    "input": "data/",
    "output": "output/parsed/",
    "pages": "output/pages/",
    "matches": "output/matches/",
    "skipped": "output/skipped/",
}
DEFAULT_MAX_FILE_SIZE_KB: int = 5120


def main() -> None:
    args: argparse.Namespace = get_args()

    if not args.match_only:
        parse_source_pdfs(args)
    if len(args.keywords):
        find_keyword_matches(args)


def get_args() -> argparse.Namespace:
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
        "-M",
        "--match-only",
        action="store_true",
        help="Skip PDF parsing; only keyword matching will be performed.",
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
        help="The relative directory containing the converted text files.",
    )
    parser.add_argument(
        "-p",
        "--progress",
        action="store_true",
        help="Display progress bars.",
    )
    parser.add_argument(
        "--reprocess",
        "-R",
        action="store_true",
        help="Reprocess any PDF files that have already been parsed.",
    )
    parser.add_argument(
        "--max-size",
        "-S",
        type=int,
        default=DEFAULT_MAX_FILE_SIZE_KB,
        help="Maximum file size to convert to text in KB. Default: 5MB",
    )
    return parser.parse_args()


def parse_source_pdfs(args: argparse.Namespace) -> None:
    files: list[str] = []
    source_directory: str = args.input_directory

    os.makedirs(os.path.dirname(source_directory), exist_ok=True)
    for filename in tqdm(os.listdir(source_directory), disable=not args.progress):
        if os.path.splitext(filename)[-1].lower() == ".pdf":
            logger.info(f"Found PDF: {filename=}")
            files.append(filename)

    logger.info(f"Processing {len(files)} file(s)")
    for filename in tqdm(files, disable=not get_args().progress):
        parse_pdf(
            filename,
            source_directory,
            max_file_size_kb=args.max_size,
            reprocess=args.reprocess,
            output_directory=args.output_directory,
        )


def parse_pdf(
    filename: str,
    directory: str,
    max_file_size_kb: int,
    reprocess: bool,
    output_directory: str,
) -> None:
    logger.info(f"Parsing: {filename=}")

    root: str
    path: str = f"{directory}/{filename}"
    filesize: int = os.path.getsize(path)

    (root, _) = os.path.splitext(filename)
    parsed_filepath: str = os.path.join(output_directory, f"{root}.txt")
    skipped_filepath: str = os.path.join(DIRECTORIES["skipped"], f"{root}.txt")

    if not reprocess and any(
        (os.path.exists(parsed_filepath), os.path.exists(skipped_filepath)),
    ):
        logger.info(f"File {filename=} has already been parsed, skipping")
        return

    if bytesto(filesize) > max_file_size_kb:
        logger.info(f"File {filename} exceeds {max_file_size_kb} limit, skipping")
        os.makedirs(os.path.dirname(DIRECTORIES["skipped"]), exist_ok=True)
        with open(skipped_filepath, "a") as fp:
            fp.write(f"SKIPPED {filename=}, byte size {filesize=}kb")
        return

    try:
        convert_pdf_to_txt(path, root, parsed_filepath, output_directory)
    except Exception as exc:
        logger.error(exc)
        raise

    remove_converted_pdf_images()

    logger.info(f"Finished writing file: {parsed_filepath}")


def find_keyword_matches(args: argparse.Namespace) -> None:
    files: list[str] = []
    match_count: int = 0
    output_directory: str = args.output_directory

    os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    for filename in tqdm(os.listdir(output_directory), disable=not get_args().progress):
        if os.path.splitext(filename)[-1].lower() == ".txt":
            logger.info(f"Found file: {filename}")
            files.append(filename)

    logger.info(f"Processing files ({len(files)})")
    for filename in tqdm(files, disable=not get_args().progress):
        logger.info(f"Checking file {filename}")

        path: str = os.path.join(output_directory, filename)

        with open(path, "r") as fp:
            text: str = fp.read()
            exists: bool = any(term.lower() in text for term in args.keywords)
            if exists:
                logger.info(
                    f"Keyword present in file. Moving file to {DIRECTORIES['matches']}"
                )
                match_count += 1
                os.makedirs(os.path.dirname(DIRECTORIES["matches"]), exist_ok=True)
                shutil.move(path, f"{DIRECTORIES['matches']}/{filename}")

    logger.info(f"Finished processing all files. Found {match_count} keyword matches")


def convert_pdf_to_txt(
    path: str, base_name: str, parsed_filepath: str, output_directory: str
) -> None:
    try:
        pages: list[Image] = convert_from_path(path, 500)
    except Exception as exc:
        logger.error(exc)
        raise

    image_count: int = convert_pdf_to_img(pages, base_name)

    os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    with open(parsed_filepath, "a") as fp:
        for i in tqdm(range(0, image_count), disable=not get_args().progress):
            filename: str = get_pdf_as_img_filename(i, DIRECTORIES["pages"], base_name)

            text: str = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace("-\n", "")

            fp.write(text)


def convert_pdf_to_img(pages: str, base_name: str) -> int:
    image_count: int = 0

    for page in tqdm(pages, disable=not get_args().progress):
        os.makedirs(os.path.dirname(DIRECTORIES["input"]), exist_ok=True)
        filename: str = get_pdf_as_img_filename(
            image_count, DIRECTORIES["pages"], base_name
        )
        logger.info(f"Saving page (image): {filename=}")
        page.save(filename, "JPEG")
        image_count += 1

    return image_count


def remove_converted_pdf_images() -> None:
    for filename in tqdm(
        os.listdir(DIRECTORIES["pages"]), disable=not get_args().progress
    ):
        path: str = os.path.join(DIRECTORIES["pages"], filename)

        if os.path.isfile(path):
            logger.info(f"Removing file: {path}")
            os.remove(path)


def get_pdf_as_img_filename(page_num: int, path: str, base_name: str) -> str:
    return os.path.join(path, f"{base_name}_page_{page_num}.jpg")


def bytesto(bytes: int, to: str = "k", bsize: int = 1024) -> Union[int, float]:
    a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
    return bytes / (bsize ** a[to])


if __name__ == "__main__":
    main()
