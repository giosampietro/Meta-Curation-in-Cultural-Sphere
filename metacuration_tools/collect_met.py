from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List

from .review import write_html_review, write_pixplot_metadata


def build_met_scraper_command(
    repo_root: Path,
    keyword: str,
    limit: int,
    output_dir: Path,
    python_executable: str = "python3",
) -> List[str]:
    scraper = repo_root / "Methodology" / "01-data-collection " / "met_scraper.py"
    return [
        python_executable,
        str(scraper),
        "--terms",
        keyword,
        "--max",
        str(limit),
        "--output",
        str(output_dir),
    ]


def run_collection(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = Path(args.output)
    command = build_met_scraper_command(
        repo_root=repo_root,
        keyword=args.keyword,
        limit=args.limit,
        output_dir=output_dir,
        python_executable=args.python,
    )
    subprocess.run(command, check=True)
    review = write_html_review(output_dir)
    metadata = write_pixplot_metadata(output_dir)
    print(f"Review page: {review}")
    print(f"PixPlot metadata: {metadata}")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect a small Met image set and prepare review/PixPlot files."
    )
    parser.add_argument("--keyword", default="cloud", help="Met search keyword.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum Met object records to process.")
    parser.add_argument(
        "--output",
        default="data/samples/met-cloud-test",
        help="Output folder for images, metadata, review page, and PixPlot metadata.",
    )
    parser.add_argument("--python", default="python3", help="Python executable used for the original scraper.")
    args = parser.parse_args(argv)
    return run_collection(args)


if __name__ == "__main__":
    raise SystemExit(main())
