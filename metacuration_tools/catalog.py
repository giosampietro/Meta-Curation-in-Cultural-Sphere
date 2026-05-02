from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List

from .sources import SourceImage


class SerpentCatalog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS source_images (
                    source TEXT NOT NULL,
                    source_record_id TEXT NOT NULL,
                    image_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    creator TEXT NOT NULL,
                    date TEXT NOT NULL,
                    culture TEXT NOT NULL,
                    department TEXT NOT NULL,
                    object_url TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    rights TEXT NOT NULL,
                    license TEXT NOT NULL,
                    search_term TEXT NOT NULL,
                    theme_layer TEXT NOT NULL,
                    inclusion_reason TEXT NOT NULL,
                    description TEXT NOT NULL,
                    download_status TEXT NOT NULL DEFAULT 'pending',
                    local_filename TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (source, source_record_id, image_url)
                )
                """
            )

    def upsert_records(self, records: Iterable[SourceImage]) -> int:
        inserted = 0
        with self._connect() as conn:
            for record in records:
                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO source_images (
                        source, source_record_id, image_id, title, creator, date,
                        culture, department, object_url, image_url, rights, license,
                        search_term, theme_layer, inclusion_reason, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.source,
                        record.source_record_id,
                        record.image_id,
                        record.title,
                        record.creator,
                        record.date,
                        record.culture,
                        record.department,
                        record.object_url,
                        record.image_url,
                        record.rights,
                        record.license,
                        record.search_term,
                        record.theme_layer,
                        record.inclusion_reason,
                        record.description,
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def list_records(self) -> List[SourceImage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT source, source_record_id, image_id, title, creator, date,
                       culture, department, object_url, image_url, rights, license,
                       search_term, theme_layer, inclusion_reason, description
                FROM source_images
                ORDER BY source, source_record_id, image_id, image_url
                """
            ).fetchall()
        return [SourceImage(**dict(row)) for row in rows]

    def mark_downloaded(self, record: SourceImage, filename: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE source_images
                SET download_status = 'downloaded', local_filename = ?
                WHERE source = ? AND source_record_id = ? AND image_url = ?
                """,
                (filename, record.source, record.source_record_id, record.image_url),
            )

    def mark_failed(self, record: SourceImage) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE source_images
                SET download_status = 'failed'
                WHERE source = ? AND source_record_id = ? AND image_url = ?
                """,
                (record.source, record.source_record_id, record.image_url),
            )
