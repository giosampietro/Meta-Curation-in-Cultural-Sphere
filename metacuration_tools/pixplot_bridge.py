from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List

from .review import write_pixplot_metadata


def default_pixplot_out_dir(collection: Path) -> Path:
    return Path("data") / "pixplot" / Path(collection).name


def build_pixplot_command(
    images_dir: Path,
    metadata_csv: Path,
    out_dir: Path,
    max_images: int | None = None,
    n_neighbors: int = 6,
    min_dist: float = 0.1,
    metric: str = "cosine",
    min_cluster_size: int = 3,
    cell_size: int = 32,
) -> List[str]:
    command = [
        "pixplot",
        "--images",
        str(Path(images_dir) / "*"),
        "--metadata",
        str(metadata_csv),
        "--out_dir",
        str(out_dir),
        "--n_neighbors",
        str(n_neighbors),
        "--min_dist",
        str(min_dist),
        "--metric",
        metric,
        "--min_cluster_size",
        str(min_cluster_size),
        "--cell_size",
        str(cell_size),
    ]
    if max_images is not None:
        command.extend(["--max_images", str(max_images)])
    return command


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and optionally run PixPlot for a collected image folder."
    )
    parser.add_argument("--collection", default="data/samples/met-cloud-test")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--max-images", type=int, default=5000)
    parser.add_argument("--n-neighbors", type=int, default=6)
    parser.add_argument("--min-dist", type=float, default=0.1)
    parser.add_argument("--metric", default="cosine")
    parser.add_argument("--min-cluster-size", type=int, default=3)
    parser.add_argument("--cell-size", type=int, default=32)
    parser.add_argument("--execute", action="store_true", help="Run PixPlot if it is installed.")
    args = parser.parse_args(argv)

    collection = Path(args.collection)
    out_dir = Path(args.out_dir) if args.out_dir else default_pixplot_out_dir(collection)
    metadata_csv = write_pixplot_metadata(collection)
    command = build_pixplot_command(
        images_dir=collection / "images",
        metadata_csv=metadata_csv,
        out_dir=out_dir,
        max_images=args.max_images,
        n_neighbors=args.n_neighbors,
        min_dist=args.min_dist,
        metric=args.metric,
        min_cluster_size=args.min_cluster_size,
        cell_size=args.cell_size,
    )

    print("PixPlot metadata:", metadata_csv)
    print("PixPlot command:")
    print(" ".join(command))

    if not args.execute:
        print("Dry run only. Add --execute to run PixPlot after installing it.")
        return 0

    if shutil.which("pixplot") is None:
        print("PixPlot is not installed. Install it with requirements-pixplot.txt, preferably in a separate environment.")
        return 2

    subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
