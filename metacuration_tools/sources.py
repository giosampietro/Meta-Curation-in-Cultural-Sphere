from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List
from urllib.parse import urlparse


Downloader = Callable[[str], bytes]


def _clean_slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:120] or "record"


def _extension_from_url(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return ".jpg"


@dataclass(frozen=True)
class SourceImage:
    source: str
    source_record_id: str
    image_id: str = ""
    title: str = "Untitled"
    creator: str = ""
    date: str = ""
    culture: str = ""
    department: str = ""
    object_url: str = ""
    image_url: str = ""
    rights: str = ""
    license: str = ""
    search_term: str = ""
    theme_layer: str = "core"
    inclusion_reason: str = ""
    description: str = ""

    @property
    def image_key(self) -> str:
        if self.image_id:
            image_part = self.image_id
        else:
            image_part = hashlib.sha1(self.image_url.encode("utf-8")).hexdigest()[:12]
        return _clean_slug(f"{self.source}_{self.source_record_id}_{image_part}")

    def filename(self) -> str:
        return f"{self.image_key}{_extension_from_url(self.image_url)}"

    def metadata(self, filename: str | None = None) -> dict:
        filename = filename or self.filename()
        return {
            "id": Path(filename).stem,
            "objectID": Path(filename).stem,
            "filename": filename,
            "source": self.source,
            "source_record_id": self.source_record_id,
            "image_id": self.image_id,
            "title": self.title or "Untitled",
            "creator": self.creator,
            "artistDisplayName": self.creator,
            "date": self.date,
            "objectDate": self.date,
            "culture": self.culture,
            "department": self.department or self.source,
            "objectURL": self.object_url,
            "image_url": self.image_url,
            "rights": self.rights,
            "license": self.license,
            "search_term": self.search_term,
            "theme_layer": self.theme_layer,
            "inclusion_reason": self.inclusion_reason,
            "description": self.description or self.title or "Untitled",
            "tags": [self.source, self.theme_layer, self.search_term],
        }


def write_collection_records(
    collection_dir: Path,
    records: Iterable[SourceImage],
    downloader: Downloader,
) -> List[str]:
    collection_dir = Path(collection_dir)
    images_dir = collection_dir / "images"
    metadata_dir = collection_dir / "metadata"
    images_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for record in records:
        filename = record.filename()
        image_path = images_dir / filename
        metadata_path = metadata_dir / f"{Path(filename).stem}.json"
        if not image_path.exists():
            image_path.write_bytes(downloader(record.image_url))
        metadata_path.write_text(
            json.dumps(record.metadata(filename), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        written.append(filename)
    return written
