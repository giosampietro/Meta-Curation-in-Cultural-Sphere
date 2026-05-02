import csv
import json
import tempfile
import unittest
from pathlib import Path

from metacuration_tools.collect_met import build_met_scraper_command
from metacuration_tools.pixplot_bridge import build_pixplot_command, default_pixplot_out_dir
from metacuration_tools.review import write_html_review, write_pixplot_metadata


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


if __name__ == "__main__":
    unittest.main()
