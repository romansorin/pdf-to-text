from __future__ import annotations

import argparse
import logging
import os
import shutil
from typing import Union

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from rapidfuzz import fuzz
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger("pdftotext")

DIRECTORIES: dict[str, str] = {
    "output": "output/",
    "converted": "converted/",
    "matches": "matches/",
    "skipped": "skipped/",
}


def parse_source_pdfs(args: argparse.Namespace) -> None:
    files: list[str] = []
    path: str = args.path

    if not os.path.exists(path):
        raise FileNotFoundError(f"File or directory with path {path!r} does not exist.")

    if os.path.isfile(path):
        (root, ext) = os.path.splitext(path)

        if ext.lower() == ".pdf":
            files.append(os.path.basename(path))
        else:
            raise ValueError(f"File has extension {ext!r}; must be of type pdf")
    else:
        for filename in tqdm(os.listdir(path), disable=not args.progress):
            if os.path.splitext(filename)[1].lower() == ".pdf":
                logger.debug(f"Found PDF: {filename=}")
                files.append(filename)

    initial_file_count: int = len(files)
    logger.info(f"Parsing {initial_file_count} PDF file(s)")
    # TODO: improve with a skip count, reprocessed count, etc.
    parsed_file_count: int = 0

    for filename in tqdm(files, disable=not args.progress):
        parsed: bool = parse_pdf(
            filename,
            os.path.dirname(path) if os.path.isfile(path) else path,
            max_file_size_kb=args.max_size,
            reprocess=args.reprocess,
            output_directory=args.output_directory,
            keep_converted=args.keep_converted,
            progress=args.progress,
        )
        if parsed:
            parsed_file_count += 1

    logger.info(f"Finished parsing {parsed_file_count} PDF file(s)")


def parse_pdf(
    filename: str,
    directory: str,
    max_file_size_kb: int,
    reprocess: bool,
    output_directory: str,
    keep_converted: bool,
    progress: bool = False,
) -> bool:
    logger.debug(f"Parsing: {filename=}")

    root: str
    path: str = f"{directory}/{filename}"
    filesize: int = os.path.getsize(path)

    (root, _) = os.path.splitext(filename)
    parsed_filepath: str = os.path.join(output_directory, f"{root}.txt")
    skipped_filepath: str = os.path.join(
        output_directory, DIRECTORIES["skipped"], f"{root}.txt"
    )

    if not reprocess and any(
        (os.path.exists(parsed_filepath), os.path.exists(skipped_filepath)),
    ):
        logger.debug(f"File {filename=} has already been parsed, skipping")
        return False

    if bytesto(filesize) > max_file_size_kb:
        logger.debug(f"File {filename=} exceeds {max_file_size_kb=} limit, skipping")
        os.makedirs(
            os.path.dirname(os.path.join(output_directory, DIRECTORIES["skipped"])),
            exist_ok=True,
        )
        with open(skipped_filepath, "a") as fp:
            fp.write(f"{filename=}:{filesize=}")
        return False

    try:
        convert_pdf_to_txt(
            path, root, parsed_filepath, output_directory, progress=progress
        )
    except Exception as exc:
        logger.error(exc)
        raise

    if not keep_converted:
        remove_converted_pdf_images(output_directory, progress=progress)

    logger.debug(f"Finished writing to {parsed_filepath=}")
    return True


def find_keyword_matches(args: argparse.Namespace) -> None:
    files: list[str] = []
    match_count: int = 0
    output_directory: str = args.output_directory
    matches_directory: str = os.path.join(output_directory, DIRECTORIES["matches"])

    os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    for filename in tqdm(os.listdir(output_directory), disable=not args.progress):
        if os.path.splitext(filename)[1].lower() == ".txt":
            logger.debug(f"Found file: {filename}")
            files.append(filename)

    logger.info(f"Checking for keyword matches in {len(files)} file(s)")

    for filename in tqdm(files, disable=not args.progress):
        logger.debug(f"Checking file {filename}")

        path: str = os.path.join(output_directory, filename)

        with open(path, "r") as fp:
            contents: str = fp.read()

            # TODO: implement fuzzy matching, arbitrary similarity ratio, CLI arg
            similarity_ratio: float = any(
                fuzz.token_set_ratio(contents, term) > 80 for term in args.keywords
            )

            if any(term in contents for term in args.keywords):
                logger.debug(
                    f"Keyword found in {path=}; moving to {matches_directory!r}"
                )

                os.makedirs(os.path.dirname(matches_directory), exist_ok=True)
                shutil.move(path, os.path.join(matches_directory, filename))

                match_count += 1

    logger.info(
        f"Finished processing all files. Found {match_count} keyword match(es)."
    )


def convert_pdf_to_txt(
    path: str,
    base_name: str,
    parsed_filepath: str,
    output_directory: str,
    progress: bool = False,
) -> None:
    try:
        converted_pages: list[Image] = convert_from_path(path, 500)
    except Exception as exc:
        logger.error(exc)
        raise

    image_count: int = convert_pdf_to_img(
        converted_pages, base_name, output_directory, progress=progress
    )

    os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    with open(parsed_filepath, "a") as fp:
        for i in tqdm(range(0, image_count), disable=not progress):
            filename: str = get_pdf_as_img_filename(
                i,
                os.path.join(output_directory, DIRECTORIES["converted"]),
                base_name,
            )

            text: str = pytesseract.image_to_string(Image.open(filename))
            text = text.replace("-\n", "")

            fp.write(text)


def convert_pdf_to_img(
    converted_pages: list[Image],
    base_name: str,
    output_directory: str,
    progress: bool = False,
) -> int:
    image_count: int = 0
    converted_directory: str = os.path.join(output_directory, DIRECTORIES["converted"])

    for page in tqdm(converted_pages, disable=not progress):
        os.makedirs(os.path.dirname(converted_directory), exist_ok=True)
        filename: str = get_pdf_as_img_filename(
            image_count,
            converted_directory,
            base_name,
        )
        logger.debug(f"Saving page (image): {filename=}")
        page.save(filename, "JPEG")
        image_count += 1

    return image_count


def remove_converted_pdf_images(output_directory: str, progress: bool = False) -> None:
    converted_directory: str = os.path.join(output_directory, DIRECTORIES["converted"])

    for filename in tqdm(os.listdir(converted_directory), disable=not progress):
        path: str = os.path.join(converted_directory, filename)

        if os.path.isfile(path):
            logger.debug(f"Removing file: {path=}")
            os.remove(path)

    os.rmdir(converted_directory)


def get_pdf_as_img_filename(page_num: int, path: str, base_name: str) -> str:
    return os.path.join(path, f"{base_name}_{page_num}.jpg")


def bytesto(bytes: int, to: str = "k", bsize: int = 1024) -> Union[int, float]:
    a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
    return bytes / (bsize ** a[to])
