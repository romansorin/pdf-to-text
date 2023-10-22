from __future__ import annotations

import argparse
import logging

from .pdftotext import find_keyword_matches, parse_source_pdfs

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
DEFAULT_MAX_FILE_SIZE_KB: int = 5120


class PdfToText:
    def get_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "path",
            type=str,
            help="Path of the PDF file/directory to parse.",
        )

        parser.add_argument(
            "-K",
            "--keywords",
            nargs="+",
            default=[],
            help=(
                "A list of keywords to search for in parsed text files (case-sensitive). "
                f"Matching files will be moved to the {DIRECTORIES['matches']!r} directory."
            ),
        )
        parser.add_argument(
            "-M",
            "--match-only",
            action="store_true",
            help="Skip PDF parsing; only keyword matching will be performed.",
        )
        parser.add_argument(
            "-O",
            "--output-directory",
            type=str,
            default=DIRECTORIES["output"],
            help="The relative directory where converted/matching text files are output.",
        )
        parser.add_argument(
            "-R",
            "--reprocess",
            action="store_true",
            help="Reprocess any PDF files that have already been parsed.",
        )
        parser.add_argument(
            "-X",
            "--max-size",
            type=int,
            default=DEFAULT_MAX_FILE_SIZE_KB,
            help="Maximum file size to convert to text in KB. Default: 5MB",
        )
        parser.add_argument(
            "-k",
            "--keep-converted",
            action="store_true",
            help="Don't delete images converted from PDF (useful for debugging).",
        )
        parser.add_argument(
            "-p",
            "--progress",
            action="store_true",
            help="Display progress bars.",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enables verbose log statements.",
        )
        return parser.parse_args()

    def run(self) -> None:
        args: argparse.Namespace = self.get_args()

        if args.verbose:
            logger.setLevel(logging.DEBUG)

        if not args.match_only:
            parse_source_pdfs(args)

        if len(args.keywords):
            find_keyword_matches(args)


def main() -> None:
    pdf_to_text = PdfToText()
    pdf_to_text.run()


if __name__ == "__main__":
    main()
