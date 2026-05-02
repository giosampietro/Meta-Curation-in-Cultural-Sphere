import csv
import json
import tempfile
import unittest
from pathlib import Path

from metacuration_tools.collect_met import build_met_scraper_command
from metacuration_tools.catalog import SerpentCatalog
from metacuration_tools.pixplot_ui import patch_pixplot_toggles
from metacuration_tools.pixplot_bridge import build_pixplot_command, default_pixplot_out_dir
from metacuration_tools.review import write_html_review, write_pixplot_metadata
from metacuration_tools.serpent_collection import select_balanced_records
from metacuration_tools.source_connectors import (
    OpenSourceConnector,
    aic_record_to_source_image,
    cma_record_to_source_image,
    met_object_to_source_images,
    vam_record_to_source_image,
)
from metacuration_tools.sources import SourceImage, write_collection_records


class MetacurationToolsTest(unittest.TestCase):
    def make_sample_collection(self, root: Path) -> Path:
        collection = root / "met-cloud-test"
        images = collection / "images"
        metadata = collection / "metadata"
        images.mkdir(parents=True)
        metadata.mkdir(parents=True)

        (images / "123.jpg").write_bytes(b"fake primary")
        (images / "123_additional_1.jpg").write_bytes(b"fake additional")
        (images / "123_additional_2.JPG").write_bytes(b"fake uppercase extension")
        (metadata / "123.json").write_text(
            json.dumps(
                {
                    "objectID": 123,
                    "title": "Cloud Study",
                    "artistDisplayName": "Example Artist",
                    "objectDate": "1824",
                    "objectBeginDate": 1824,
                    "department": "European Paintings",
                    "medium": "Oil on paper",
                    "objectURL": "https://www.metmuseum.org/art/collection/search/123",
                    "tags": [{"term": "Clouds"}, {"term": "Sky"}],
                }
            ),
            encoding="utf-8",
        )
        return collection

    def test_write_html_review_creates_human_readable_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            collection = self.make_sample_collection(Path(tmp))

            output = write_html_review(collection)

            html = output.read_text(encoding="utf-8")
            self.assertIn("Met Collection Review", html)
            self.assertIn("Cloud Study", html)
            self.assertIn("Example Artist", html)
            self.assertIn("images/123.jpg", html)
            self.assertIn("https://www.metmuseum.org/art/collection/search/123", html)

    def test_write_pixplot_metadata_exports_one_row_per_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            collection = self.make_sample_collection(Path(tmp))

            output = write_pixplot_metadata(collection)

            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                ["123.jpg", "123_additional_1.jpg", "123_additional_2.JPG"],
                [row["filename"] for row in rows],
            )
            self.assertEqual(
                ["European Paintings", "European Paintings", "European Paintings"],
                [row["category"] for row in rows],
            )
            self.assertEqual("Clouds|Sky", rows[0]["tags"])
            self.assertEqual("Cloud Study | Example Artist | Oil on paper", rows[0]["description"])
            self.assertEqual("1824", rows[0]["year"])

    def test_pixplot_command_uses_original_project_clustering_parameters(self):
        command = build_pixplot_command(
            images_dir=Path("data/samples/met-cloud-test/images"),
            metadata_csv=Path("data/samples/met-cloud-test/pixplot_metadata.csv"),
            out_dir=Path("data/pixplot/met-cloud-test"),
            max_images=5000,
            n_neighbors=6,
            min_dist=0.1,
            metric="cosine",
            min_cluster_size=3,
        )

        self.assertEqual(command[0], "pixplot")
        self.assertIn("--images", command)
        self.assertIn("data/samples/met-cloud-test/images/*", command)
        self.assertIn("--metadata", command)
        self.assertIn("--out_dir", command)
        self.assertIn("--n_neighbors", command)
        self.assertIn("6", command)
        self.assertIn("--min_dist", command)
        self.assertIn("0.1", command)
        self.assertIn("--metric", command)
        self.assertIn("cosine", command)
        self.assertIn("--min_cluster_size", command)
        self.assertIn("3", command)

    def test_default_pixplot_output_dir_uses_collection_name(self):
        self.assertEqual(
            Path("data/pixplot/met-cloud-phase2"),
            default_pixplot_out_dir(Path("data/samples/met-cloud-phase2")),
        )

    def test_met_runner_wraps_original_met_scraper(self):
        command = build_met_scraper_command(
            repo_root=Path("/repo"),
            keyword="cloud",
            limit=2,
            output_dir=Path("data/samples/met-cloud-test"),
        )

        self.assertEqual(command[0], "python3")
        self.assertEqual(command[1], "/repo/Methodology/01-data-collection /met_scraper.py")
        self.assertEqual(command[-6:], ["--terms", "cloud", "--max", "2", "--output", "data/samples/met-cloud-test"])

    def test_source_image_writes_normalized_metadata_and_local_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            collection = Path(tmp) / "serpents-test"
            record = SourceImage(
                source="met",
                source_record_id="123",
                image_id="primary",
                title="Bronze serpent",
                creator="Unknown",
                date="1550",
                culture="Italian",
                department="Decorative Arts",
                object_url="https://example.org/object/123",
                image_url="https://example.org/serpent.jpg",
                rights="Public Domain",
                license="CC0",
                search_term="serpent",
                theme_layer="core",
                inclusion_reason="direct keyword: serpent",
            )

            written = write_collection_records(
                collection,
                [record],
                downloader=lambda _url: b"fake image bytes",
            )

            self.assertEqual(1, len(written))
            image_path = collection / "images" / written[0]
            metadata_path = collection / "metadata" / f"{Path(written[0]).stem}.json"
            self.assertTrue(image_path.exists())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual("met", metadata["source"])
            self.assertEqual("core", metadata["theme_layer"])
            self.assertEqual("serpent", metadata["search_term"])
            self.assertEqual("https://example.org/object/123", metadata["objectURL"])

    def test_serpent_catalog_dedupes_same_source_image_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = SerpentCatalog(Path(tmp) / "catalog.sqlite")
            first = SourceImage(
                source="met",
                source_record_id="123",
                image_id="primary",
                title="Snake",
                image_url="https://example.org/snake.jpg",
                search_term="snake",
                theme_layer="core",
                inclusion_reason="direct keyword: snake",
            )
            duplicate = SourceImage(
                source="met",
                source_record_id="123",
                image_id="primary",
                title="Snake",
                image_url="https://example.org/snake.jpg",
                search_term="snakes",
                theme_layer="core",
                inclusion_reason="direct keyword: snakes",
            )

            self.assertEqual(1, catalog.upsert_records([first]))
            self.assertEqual(0, catalog.upsert_records([duplicate]))
            rows = catalog.list_records()
            self.assertEqual(1, len(rows))
            self.assertEqual("snake", rows[0].search_term)

    def test_pixplot_metadata_includes_source_layer_and_search_term(self):
        with tempfile.TemporaryDirectory() as tmp:
            collection = Path(tmp) / "serpents-test"
            write_collection_records(
                collection,
                [
                    SourceImage(
                        source="vam",
                        source_record_id="O1",
                        image_id="img",
                        title="Snake ornament",
                        image_url="https://example.org/snake.jpg",
                        search_term="snake",
                        theme_layer="core",
                        inclusion_reason="direct keyword: snake",
                    )
                ],
                downloader=lambda _url: b"fake",
            )

            output = write_pixplot_metadata(collection)

            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual("vam", rows[0]["source"])
            self.assertEqual("core", rows[0]["theme_layer"])
            self.assertEqual("snake", rows[0]["search_term"])

    def test_patch_pixplot_toggles_injects_source_and_layer_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            atlas = Path(tmp) / "atlas"
            assets = atlas / "assets" / "js"
            assets.mkdir(parents=True)
            (atlas / "index.html").write_text(
                "<html><body><script src='assets/js/tsne.js'></script></body></html>",
                encoding="utf-8",
            )

            patch_pixplot_toggles(atlas)

            index = (atlas / "index.html").read_text(encoding="utf-8")
            script = (assets / "metacuration-toggles.js").read_text(encoding="utf-8")
            self.assertIn("metacuration-toggles.js", index)
            self.assertIn("theme_layer", script)
            self.assertIn("source", script)
            self.assertIn("resetGroupIfEmpty", script)

    def test_connectors_normalize_open_source_records(self):
        met_images = met_object_to_source_images(
            {
                "objectID": 10,
                "title": "Serpent Vessel",
                "artistDisplayName": "Unknown",
                "objectDate": "1700",
                "culture": "Italian",
                "department": "Decorative Arts",
                "objectURL": "https://met.example/10",
                "primaryImage": "https://images.example/met/10.jpg",
                "additionalImages": ["https://images.example/met/10-2.jpg"],
                "isPublicDomain": True,
            },
            search_term="serpent",
            theme_layer="core",
        )
        self.assertEqual(["primary", "additional_1"], [image.image_id for image in met_images])
        self.assertEqual("met", met_images[0].source)
        self.assertEqual("Public Domain", met_images[0].rights)

        vam = vam_record_to_source_image(
            {
                "systemNumber": "O355355",
                "objectType": "Snake",
                "_primaryMaker": {"name": "Unknown"},
                "_primaryDate": "1916-1919",
                "_primaryPlace": "Turkey",
                "_primaryImageId": "2019ME9071",
                "_images": {"_iiif_image_base_url": "https://framemark.vam.ac.uk/collections/2019ME9071/"},
            },
            search_term="snake",
            theme_layer="core",
        )
        self.assertEqual("vam", vam.source)
        self.assertIn("!1200,1200", vam.image_url)

        aic = aic_record_to_source_image(
            {
                "id": 20579,
                "title": "Hercules and the Lernaean Hydra",
                "artist_display": "Gustave Moreau",
                "date_display": "1875-76",
                "department_title": "Painting and Sculpture of Europe",
                "image_id": "2ae64c8a",
                "is_public_domain": True,
            },
            search_term="hydra",
            theme_layer="expanded",
        )
        self.assertEqual("aic", aic.source)
        self.assertEqual("expanded", aic.theme_layer)
        self.assertIn("lakeimagesweb.artic.edu/iiif/2/2ae64c8a", aic.image_url)

        cma = cma_record_to_source_image(
            {
                "id": 137667,
                "title": "The prince enters the service of a snake",
                "creation_date": "c. 1560",
                "culture": ["Mughal India"],
                "department": "Indian and Southeast Asian Art",
                "url": "https://www.clevelandart.org/art/1962.279.245.b",
                "images": {"web": {"url": "https://images.clevelandart.org/1962.jpg"}},
                "share_license_status": "CC0",
            },
            search_term="snake",
            theme_layer="core",
        )
        self.assertEqual("cma", cma.source)
        self.assertEqual("CC0", cma.license)

    def test_vam_connector_paginates_to_requested_limit(self):
        connector = OpenSourceConnector("vam", polite_delay=0)
        calls = []

        def fake_get_json(_url, params=None):
            calls.append(params)
            page = params["page"]
            records = [
                {
                    "systemNumber": f"O{page}-{idx}",
                    "objectType": "Snake",
                    "_primaryImageId": f"IMG{page}-{idx}",
                    "_images": {"_iiif_image_base_url": f"https://example.org/{page}/{idx}/"},
                }
                for idx in range(100)
            ]
            return {"records": records, "info": {"record_count": 250}}

        object.__setattr__(connector, "get_json", fake_get_json)

        records = connector.search("snake", "core", 150)

        self.assertEqual(150, len(records))
        self.assertEqual([1, 2], [call["page"] for call in calls])

    def test_aic_connector_paginates_to_requested_limit(self):
        connector = OpenSourceConnector("aic", polite_delay=0)
        calls = []

        def fake_get_json(url, params=None):
            del params
            calls.append(url)
            page = 1 if '"page":1' in url else 2
            return {
                "pagination": {"total": 150, "total_pages": 2},
                "data": [
                    {
                        "id": page * 1000 + idx,
                        "title": "Serpent",
                        "image_id": f"image-{page}-{idx}",
                        "is_public_domain": True,
                    }
                    for idx in range(100)
                ],
            }

        object.__setattr__(connector, "get_json", fake_get_json)

        records = connector.search("serpent", "core", 150)

        self.assertEqual(150, len(records))
        self.assertEqual(2, len(calls))

    def test_balanced_selection_round_robins_sources(self):
        records = [
            SourceImage(source="met", source_record_id=f"m{i}", image_url=f"https://example.org/m{i}.jpg")
            for i in range(5)
        ] + [
            SourceImage(source="vam", source_record_id=f"v{i}", image_url=f"https://example.org/v{i}.jpg")
            for i in range(2)
        ] + [
            SourceImage(source="aic", source_record_id="a1", image_url="https://example.org/a1.jpg")
        ]

        selected = select_balanced_records(records, 6)

        self.assertEqual(["aic", "met", "vam", "met", "vam", "met"], [record.source for record in selected])


if __name__ == "__main__":
    unittest.main()
