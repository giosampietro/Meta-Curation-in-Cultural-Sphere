from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Iterable, List
from urllib.parse import quote

import requests
from requests import RequestException

from .sources import SourceImage


USER_AGENT = "MetaCurationSerpentAtlas/0.1"


CORE_TERMS = ["snake", "snakes", "serpent", "serpents", "serpenti"]
EXPANDED_TERMS = [
    "hydra",
    "naga",
    "nagaraja",
    "ouroboros",
    "Medusa",
    "Laocoon",
    "Eden",
    "Saint George",
    "Kaliya",
    "Quetzalcoatl",
    "Asclepius",
    "dragon",
]


def _first(value) -> str:
    if isinstance(value, list):
        if not value:
            return ""
        value = value[0]
    if isinstance(value, dict):
        return str(value.get("value") or value.get("name") or "")
    return str(value or "")


def met_object_to_source_images(metadata: dict, search_term: str, theme_layer: str) -> List[SourceImage]:
    object_id = str(metadata.get("objectID") or "")
    base = {
        "source": "met",
        "source_record_id": object_id,
        "title": metadata.get("title") or "Untitled",
        "creator": metadata.get("artistDisplayName") or "",
        "date": metadata.get("objectDate") or "",
        "culture": metadata.get("culture") or "",
        "department": metadata.get("department") or "",
        "object_url": metadata.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{object_id}",
        "rights": "Public Domain" if metadata.get("isPublicDomain") else "",
        "license": "Public Domain" if metadata.get("isPublicDomain") else "",
        "search_term": search_term,
        "theme_layer": theme_layer,
        "inclusion_reason": f"{theme_layer} term: {search_term}",
        "description": metadata.get("medium") or "",
    }
    images = []
    if metadata.get("primaryImage"):
        images.append(SourceImage(**base, image_id="primary", image_url=metadata["primaryImage"]))
    for idx, url in enumerate(metadata.get("additionalImages") or [], start=1):
        if url:
            images.append(SourceImage(**base, image_id=f"additional_{idx}", image_url=url))
    return images


def vam_record_to_source_image(record: dict, search_term: str, theme_layer: str) -> SourceImage:
    system_number = str(record.get("systemNumber") or "")
    images = record.get("_images") or {}
    base_url = images.get("_iiif_image_base_url") or ""
    image_url = f"{base_url}full/!1200,1200/0/default.jpg" if base_url else images.get("_primary_thumbnail", "")
    return SourceImage(
        source="vam",
        source_record_id=system_number,
        image_id=str(record.get("_primaryImageId") or "primary"),
        title=record.get("_primaryTitle") or record.get("objectType") or "Untitled",
        creator=_first(record.get("_primaryMaker")),
        date=record.get("_primaryDate") or "",
        culture=record.get("_primaryPlace") or "",
        department=record.get("objectType") or "",
        object_url=f"https://collections.vam.ac.uk/item/{system_number}/",
        image_url=image_url,
        rights="Check V&A record",
        license="",
        search_term=search_term,
        theme_layer=theme_layer,
        inclusion_reason=f"{theme_layer} term: {search_term}",
        description=record.get("objectType") or "",
    )


def aic_record_to_source_image(record: dict, search_term: str, theme_layer: str) -> SourceImage:
    image_id = str(record.get("image_id") or "")
    return SourceImage(
        source="aic",
        source_record_id=str(record.get("id") or ""),
        image_id=image_id,
        title=record.get("title") or "Untitled",
        creator=record.get("artist_display") or "",
        date=record.get("date_display") or "",
        culture="",
        department=record.get("department_title") or "",
        object_url=f"https://www.artic.edu/artworks/{record.get('id')}",
        image_url=f"https://lakeimagesweb.artic.edu/iiif/2/{image_id}/full/!1200,1200/0/default.jpg" if image_id else "",
        rights="Public Domain" if record.get("is_public_domain") else "",
        license="Public Domain" if record.get("is_public_domain") else "",
        search_term=search_term,
        theme_layer=theme_layer,
        inclusion_reason=f"{theme_layer} term: {search_term}",
        description=record.get("thumbnail", {}).get("alt_text", "") if isinstance(record.get("thumbnail"), dict) else "",
    )


def cma_record_to_source_image(record: dict, search_term: str, theme_layer: str) -> SourceImage:
    images = record.get("images") or {}
    web = images.get("web") or images.get("print") or {}
    culture = record.get("culture") or []
    return SourceImage(
        source="cma",
        source_record_id=str(record.get("id") or ""),
        image_id=str(record.get("accession_number") or "primary"),
        title=record.get("title") or "Untitled",
        creator=", ".join(artist.get("description", "") for artist in record.get("creators", []) if artist.get("description")),
        date=record.get("creation_date") or "",
        culture="; ".join(culture) if isinstance(culture, list) else str(culture or ""),
        department=record.get("department") or "",
        object_url=record.get("url") or "",
        image_url=web.get("url") or "",
        rights=record.get("share_license_status") or "",
        license=record.get("share_license_status") or "",
        search_term=search_term,
        theme_layer=theme_layer,
        inclusion_reason=f"{theme_layer} term: {search_term}",
        description=record.get("description") or record.get("tombstone") or "",
    )


@dataclass(frozen=True)
class OpenSourceConnector:
    source: str
    polite_delay: float = 0.15

    def headers(self) -> dict:
        if self.source == "aic":
            return {"User-Agent": USER_AGENT, "AIC-User-Agent": "MetaCuration local research"}
        return {"User-Agent": USER_AGENT}

    def get_json(self, url: str, params: dict | None = None) -> dict:
        response = requests.get(url, params=params, headers=self.headers(), timeout=45)
        response.raise_for_status()
        if self.polite_delay:
            time.sleep(self.polite_delay)
        return response.json()

    def search(self, search_term: str, theme_layer: str, limit: int) -> List[SourceImage]:
        if self.source == "met":
            return self._search_met(search_term, theme_layer, limit)
        if self.source == "vam":
            return self._search_vam(search_term, theme_layer, limit)
        if self.source == "aic":
            return self._search_aic(search_term, theme_layer, limit)
        if self.source == "cma":
            return self._search_cma(search_term, theme_layer, limit)
        raise ValueError(f"Unsupported source: {self.source}")

    def count(self, search_term: str, theme_layer: str = "core") -> int:
        if self.source == "met":
            data = self.get_json(
                "https://collectionapi.metmuseum.org/public/collection/v1/search",
                {"hasImages": "true", "q": search_term},
            )
            return int(data.get("total") or len(data.get("objectIDs") or []))
        if self.source == "vam":
            data = self.get_json(
                "https://api.vam.ac.uk/v2/objects/search",
                {"q": search_term, "images_exist": 1, "page_size": 1},
            )
            return int(data.get("info", {}).get("record_count") or 0)
        if self.source == "aic":
            query = {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": search_term,
                                "fields": ["title^3", "description", "term_titles", "subject_titles"],
                            }
                        },
                        {"term": {"is_public_domain": True}},
                        {"exists": {"field": "image_id"}},
                    ]
                }
            }
            params = {"query": query, "limit": 0, "fields": ["id"]}
            url = "https://api.artic.edu/api/v1/artworks/search?params=" + quote(
                json.dumps(params, separators=(",", ":"))
            )
            data = self.get_json(url)
            return int(data.get("pagination", {}).get("total") or 0)
        if self.source == "cma":
            data = self.get_json(
                "https://openaccess-api.clevelandart.org/api/artworks/",
                {"q": search_term, "has_image": 1, "limit": 0},
            )
            return int(data.get("info", {}).get("total") or 0)
        raise ValueError(f"Unsupported source: {self.source}")

    def _search_met(self, search_term: str, theme_layer: str, limit: int) -> List[SourceImage]:
        data = self.get_json(
            "https://collectionapi.metmuseum.org/public/collection/v1/search",
            {"hasImages": "true", "q": search_term},
        )
        object_ids = (data.get("objectIDs") or [])[:limit]
        records: List[SourceImage] = []
        for object_id in object_ids:
            try:
                metadata = self.get_json(
                    f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
                )
            except RequestException:
                continue
            records.extend(met_object_to_source_images(metadata, search_term, theme_layer))
            if len(records) >= limit:
                break
        return records[:limit]

    def _search_vam(self, search_term: str, theme_layer: str, limit: int) -> List[SourceImage]:
        records: List[SourceImage] = []
        page_size = min(limit, 100)
        page = 1
        total_pages = 1
        while len(records) < limit and page <= total_pages:
            data = self.get_json(
                "https://api.vam.ac.uk/v2/objects/search",
                {"q": search_term, "images_exist": 1, "page_size": page_size, "page": page},
            )
            total = int(data.get("info", {}).get("record_count") or 0)
            total_pages = max(1, math.ceil(total / page_size))
            page_records = [
                vam_record_to_source_image(record, search_term, theme_layer)
                for record in data.get("records", [])
            ]
            records.extend(record for record in page_records if record.image_url)
            if not data.get("records"):
                break
            page += 1
        return records[:limit]

    def _search_aic(self, search_term: str, theme_layer: str, limit: int) -> List[SourceImage]:
        query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": search_term,
                            "fields": ["title^3", "description", "term_titles", "subject_titles"],
                        }
                    },
                    {"term": {"is_public_domain": True}},
                    {"exists": {"field": "image_id"}},
                ]
            }
        }
        records: List[SourceImage] = []
        page = 1
        total_pages = 1
        page_size = min(limit, 100)
        while len(records) < limit and page <= total_pages:
            params = {
                "query": query,
                "limit": page_size,
                "page": page,
                "fields": [
                    "id",
                    "title",
                    "image_id",
                    "is_public_domain",
                    "artist_display",
                    "date_display",
                    "department_title",
                    "thumbnail",
                ],
            }
            url = "https://api.artic.edu/api/v1/artworks/search?params=" + quote(
                json.dumps(params, separators=(",", ":"))
            )
            data = self.get_json(url)
            total_pages = int(data.get("pagination", {}).get("total_pages") or 1)
            page_records = [
                aic_record_to_source_image(record, search_term, theme_layer)
                for record in data.get("data", [])
            ]
            records.extend(record for record in page_records if record.image_url)
            if not data.get("data"):
                break
            page += 1
        return records[:limit]

    def _search_cma(self, search_term: str, theme_layer: str, limit: int) -> List[SourceImage]:
        records: List[SourceImage] = []
        page_size = min(limit, 100)
        skip = 0
        total = None
        while len(records) < limit:
            data = self.get_json(
                "https://openaccess-api.clevelandart.org/api/artworks/",
                {"q": search_term, "has_image": 1, "limit": page_size, "skip": skip},
            )
            if total is None:
                total = int(data.get("info", {}).get("total") or 0)
            page_records = [
                cma_record_to_source_image(record, search_term, theme_layer)
                for record in data.get("data", [])
            ]
            records.extend(record for record in page_records if record.image_url)
            if not data.get("data"):
                break
            skip += len(data.get("data", []))
            if skip >= total:
                break
        return records[:limit]


def collect_open_records(
    sources: Iterable[str],
    core_limit_per_term: int,
    expanded_limit_per_term: int,
) -> List[SourceImage]:
    records: List[SourceImage] = []
    for source in sources:
        connector = OpenSourceConnector(source)
        for term in CORE_TERMS:
            records.extend(connector.search(term, "core", core_limit_per_term))
        for term in EXPANDED_TERMS:
            records.extend(connector.search(term, "expanded", expanded_limit_per_term))
    return records
