from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class ImageRecord:
    filename: str
    path: Path
    object_id: str
    title: str
    creator: str
    date: str
    year: str
    category: str
    tags: str
    description: str
    permalink: str


def _metadata_files(collection_dir: Path) -> Iterable[Path]:
    return sorted((collection_dir / "metadata").glob("*.json"))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _object_id(metadata_path: Path, metadata: dict) -> str:
    return str(metadata.get("objectID") or metadata.get("id") or metadata_path.stem)


def _tags(metadata: dict) -> str:
    tags = metadata.get("tags") or []
    terms = []
    for tag in tags:
        if isinstance(tag, dict) and tag.get("term"):
            terms.append(str(tag["term"]))
        elif isinstance(tag, str):
            terms.append(tag)
    return "|".join(terms)


def _year(metadata: dict) -> str:
    value = metadata.get("objectBeginDate") or metadata.get("year") or ""
    match = re.search(r"-?\d+", str(value))
    return match.group(0) if match else ""


def _description(metadata: dict) -> str:
    parts = [
        metadata.get("title") or "Untitled",
        metadata.get("artistDisplayName") or metadata.get("creator") or "",
        metadata.get("medium") or "",
    ]
    return " | ".join(str(part) for part in parts if part)


def _image_paths_for_object(collection_dir: Path, object_id: str) -> List[Path]:
    images_dir = collection_dir / "images"
    paths = []
    for extension in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        paths.extend(images_dir.glob(f"{object_id}*{extension[1:]}"))
    return sorted(paths, key=lambda path: (path.stem != object_id, path.name))


def collect_image_records(collection_dir: Path) -> List[ImageRecord]:
    collection_dir = Path(collection_dir)
    records: List[ImageRecord] = []
    for metadata_path in _metadata_files(collection_dir):
        metadata = _read_json(metadata_path)
        object_id = _object_id(metadata_path, metadata)
        title = metadata.get("title") or "Untitled"
        creator = metadata.get("artistDisplayName") or metadata.get("creator") or ""
        date = metadata.get("objectDate") or metadata.get("date") or ""
        category = metadata.get("department") or metadata.get("source") or "Metropolitan Museum of Art"
        tags = _tags(metadata)
        description = _description(metadata)
        permalink = metadata.get("objectURL") or metadata.get("source") or ""
        year = _year(metadata)

        for image_path in _image_paths_for_object(collection_dir, object_id):
            records.append(
                ImageRecord(
                    filename=image_path.name,
                    path=image_path,
                    object_id=object_id,
                    title=str(title),
                    creator=str(creator),
                    date=str(date),
                    year=year,
                    category=str(category),
                    tags=tags,
                    description=description,
                    permalink=str(permalink),
                )
            )
    return records


def write_pixplot_metadata(collection_dir: Path, output_path: Path | None = None) -> Path:
    collection_dir = Path(collection_dir)
    output_path = output_path or collection_dir / "pixplot_metadata.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = collect_image_records(collection_dir)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["filename", "category", "tags", "description", "permalink", "year"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "filename": record.filename,
                    "category": record.category,
                    "tags": record.tags,
                    "description": record.description,
                    "permalink": record.permalink,
                    "year": record.year,
                }
            )
    return output_path


def write_html_review(collection_dir: Path, output_path: Path | None = None) -> Path:
    collection_dir = Path(collection_dir)
    output_path = output_path or collection_dir / "review.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = collect_image_records(collection_dir)
    grouped = {}
    for record in records:
        grouped.setdefault(record.object_id, []).append(record)

    sections = []
    for object_records in grouped.values():
        first = object_records[0]
        figures = "\n".join(
            f"""          <figure>
            <img src="images/{html.escape(record.filename)}" alt="{html.escape(record.title)}">
            <figcaption>{html.escape(record.filename)}</figcaption>
          </figure>"""
            for record in object_records
        )
        link = (
            f'<a href="{html.escape(first.permalink)}">Open source record</a>'
            if first.permalink
            else ""
        )
        sections.append(
            f"""      <section class="object">
        <div class="object-head">
          <div>
            <h2>{html.escape(first.title)}</h2>
            <p class="meta">{html.escape(first.creator)}{', ' if first.creator and first.date else ''}{html.escape(first.date)}. Object {html.escape(first.object_id)}.</p>
          </div>
          {link}
        </div>
        <div class="grid">
{figures}
        </div>
      </section>"""
        )

    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Met Collection Review</title>
    <style>
      body {{ margin: 0; font-family: Inter, system-ui, sans-serif; color: #171717; background: #faf9f6; }}
      main {{ width: min(1160px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }}
      h1 {{ margin: 0 0 12px; font-size: clamp(2rem, 5vw, 4rem); line-height: 1; }}
      h2 {{ margin: 0 0 8px; font-size: 1.1rem; }}
      p {{ max-width: 780px; line-height: 1.55; }}
      .meta {{ color: #666; }}
      .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin: 24px 0 34px; }}
      .stat {{ border: 1px solid #ddd; background: #fff; padding: 14px; }}
      .stat strong {{ display: block; font-size: 1.6rem; }}
      .object {{ border-top: 1px solid #ddd; padding: 28px 0; }}
      .object-head {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; margin-bottom: 16px; }}
      a {{ color: #315f72; }}
      .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }}
      figure {{ margin: 0; border: 1px solid #ddd; background: #fff; }}
      img {{ display: block; width: 100%; aspect-ratio: 1 / 1; object-fit: cover; background: #eee; }}
      figcaption {{ padding: 10px; color: #666; font-size: 0.85rem; overflow-wrap: anywhere; }}
      @media (max-width: 720px) {{ .object-head {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <p class="meta">Generated from Met scraper output</p>
        <h1>Met Collection Review</h1>
        <p>This page makes the collected image files and metadata inspectable before clustering. It is a review surface, not the final atlas.</p>
      </header>
      <section class="summary" aria-label="Collection summary">
        <div class="stat"><strong>{len(grouped)}</strong>object records</div>
        <div class="stat"><strong>{len(records)}</strong>image files</div>
      </section>
{chr(10).join(sections)}
    </main>
  </body>
</html>
"""
    output_path.write_text(document, encoding="utf-8")
    return output_path
