from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, List

import requests

from .catalog import SerpentCatalog
from .review import write_html_review, write_pixplot_metadata
from .source_connectors import CORE_TERMS, EXPANDED_TERMS, OpenSourceConnector
from .sources import SourceImage, write_collection_records


DEFAULT_SOURCES = ["met", "vam", "aic", "cma"]


def download_bytes(url: str) -> bytes:
    response = requests.get(url, headers={"User-Agent": "MetaCurationSerpentAtlas/0.1"}, timeout=60)
    response.raise_for_status()
    return response.content


def count_terms(sources: Iterable[str], terms: Iterable[str]) -> List[dict]:
    rows = []
    for source in sources:
        connector = OpenSourceConnector(source)
        for term in terms:
            try:
                count = connector.count(term)
                error = ""
            except Exception as exc:
                count = 0
                error = str(exc)
            rows.append({"source": source, "term": term, "count": count, "error": error})
    return rows


def collect_terms(
    sources: Iterable[str],
    core_terms: Iterable[str],
    expanded_terms: Iterable[str],
    core_limit_per_term: int,
    expanded_limit_per_term: int,
) -> List[SourceImage]:
    records: List[SourceImage] = []
    for source in sources:
        connector = OpenSourceConnector(source)
        for term in core_terms:
            records.extend(connector.search(term, "core", core_limit_per_term))
        for term in expanded_terms:
            records.extend(connector.search(term, "expanded", expanded_limit_per_term))
    return records


def write_count_report(rows: List[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "term", "count", "error"])
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def select_balanced_records(records: Iterable[SourceImage], target_images: int) -> List[SourceImage]:
    by_source = defaultdict(deque)
    for record in records:
        by_source[record.source].append(record)

    selected: List[SourceImage] = []
    sources = sorted(by_source)
    while len(selected) < target_images and sources:
        next_sources = []
        for source in sources:
            if len(selected) >= target_images:
                break
            queue = by_source[source]
            if queue:
                selected.append(queue.popleft())
            if queue:
                next_sources.append(source)
        sources = next_sources
    return selected


def build_collection(
    output_dir: Path,
    records: Iterable[SourceImage],
    target_images: int,
    download_workers: int = 1,
) -> dict:
    output_dir = Path(output_dir)
    catalog = SerpentCatalog(output_dir / "catalog.sqlite")
    inserted = catalog.upsert_records(records)
    selected = select_balanced_records(catalog.list_records(), target_images)
    written = []

    def download_record(record: SourceImage) -> str | None:
        try:
            filenames = write_collection_records(output_dir, [record], downloader=download_bytes)
            catalog.mark_downloaded(record, filenames[0])
            return filenames[0]
        except Exception:
            catalog.mark_failed(record)
            return None

    if download_workers > 1:
        with ThreadPoolExecutor(max_workers=download_workers) as executor:
            futures = [executor.submit(download_record, record) for record in selected]
            for future in as_completed(futures):
                filename = future.result()
                if filename:
                    written.append(filename)
    else:
        for record in selected:
            filename = download_record(record)
            if filename:
                written.append(filename)

    review = write_html_review(output_dir)
    pixplot_metadata = write_pixplot_metadata(output_dir)
    return {
        "inserted_records": inserted,
        "selected_records": len(selected),
        "downloaded_images": len(written),
        "review": str(review),
        "pixplot_metadata": str(pixplot_metadata),
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect an open-first serpent image atlas.")
    parser.add_argument("--output", default="data/samples/serpents-open-v1")
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCES))
    parser.add_argument("--core-terms", default=",".join(CORE_TERMS))
    parser.add_argument("--expanded-terms", default="")
    parser.add_argument("--core-limit-per-term", type=int, default=5)
    parser.add_argument("--expanded-limit-per-term", type=int, default=0)
    parser.add_argument("--target-images", type=int, default=100)
    parser.add_argument("--download-workers", type=int, default=1)
    parser.add_argument("--count-only", action="store_true")
    args = parser.parse_args(argv)

    sources = [source.strip() for source in args.sources.split(",") if source.strip()]
    core_terms = [term.strip() for term in args.core_terms.split(",") if term.strip()]
    expanded_terms = [term.strip() for term in args.expanded_terms.split(",") if term.strip()]
    output_dir = Path(args.output)

    if args.count_only:
        rows = count_terms(sources, core_terms + expanded_terms)
        report = write_count_report(rows, output_dir / "count_report.csv")
        for row in rows:
            suffix = f" ERROR: {row['error']}" if row["error"] else ""
            print(f"{row['source']},{row['term']},{row['count']}{suffix}")
        print(f"Count report: {report}")
        return 0

    records = collect_terms(
        sources=sources,
        core_terms=core_terms,
        expanded_terms=expanded_terms,
        core_limit_per_term=args.core_limit_per_term,
        expanded_limit_per_term=args.expanded_limit_per_term,
    )
    result = build_collection(output_dir, records, args.target_images, download_workers=max(1, args.download_workers))
    for key, value in result.items():
        print(f"{key}: {value}")
    return 0 if result["downloaded_images"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
