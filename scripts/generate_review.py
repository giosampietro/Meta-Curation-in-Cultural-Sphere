#!/usr/bin/env python3
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metacuration_tools.review import write_html_review, write_pixplot_metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate review HTML and PixPlot metadata for a collection folder.")
    parser.add_argument("--collection", default="data/samples/met-cloud-test")
    args = parser.parse_args()
    collection = Path(args.collection)
    print(f"Review page: {write_html_review(collection)}")
    print(f"PixPlot metadata: {write_pixplot_metadata(collection)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
