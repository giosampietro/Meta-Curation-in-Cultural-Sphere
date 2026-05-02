# Phase 2 Runnable Workflow

This phase keeps the original project intact while adding a small runnable layer.

## What Changed

- Added `requirements.txt` for the original scrapers' basic Python dependencies.
- Added `config/api_keys.example.json` as a safe template. Real keys should go in ignored local files.
- Added `scripts/collect_images.py` as a Met-only wrapper around the original Met scraper.
- Added `scripts/generate_review.py` to create a local browser review page and PixPlot metadata CSV.
- Added `scripts/run_pixplot.py` to prepare and optionally execute PixPlot.
- Added tests for the new wrapper and review/PixPlot metadata behavior.

## Why The Runner Is Met-Only For Now

The Met is the safest first source because it does not require an API key.

The other scrapers need API keys or repair:

- Harvard needs a key and currently does not call `main()`.
- Europeana needs a key.
- Smithsonian needs a key and `python-dotenv`.
- Cooper Hewitt needs a key and has a broken bottom-of-file call to `HarvardArtScraper`.

## Run A Small Met Collection

```bash
python3 scripts/collect_images.py --keyword cloud --limit 2 --output data/samples/met-cloud-test
```

This does three things:

1. Calls the original Met scraper.
2. Generates `review.html`.
3. Generates `pixplot_metadata.csv`.

The `--limit` value means object records, not exact image count. Some objects include additional views.

## Prepare PixPlot

```bash
python3 scripts/run_pixplot.py --collection data/samples/met-cloud-test
```

This is a dry run. It creates/refreshes PixPlot metadata and prints the PixPlot command.

## Run PixPlot After Installing It

PixPlot is optional and heavy. Install it in a separate environment if possible:

```bash
python3 -m pip install -r requirements-pixplot.txt
```

Then run:

```bash
python3 scripts/run_pixplot.py --collection data/samples/met-cloud-test --execute
```

The default parameters match the original project's intended meaning:

- `n_neighbors`: 6
- `min_dist`: 0.1
- `metric`: cosine
- `min_cluster_size`: 3

For small collections, `min_cluster_size` is lower than PixPlot's default so the tool can still reveal tentative hotspots.

## Preferred PixPlot Setup: Docker

Docker is currently the most stable way to run PixPlot on this project. It keeps the heavy machine-learning dependencies separate from the main computer setup.

Build the local PixPlot image once:

```bash
docker build -f docker/pixplot.Dockerfile -t metacuration-pixplot:local .
```

Then run the current 211-image sample:

```bash
docker run --rm -v "$PWD:/work" -w /work metacuration-pixplot:local python scripts/run_pixplot.py --collection data/samples/met-cloud-200 --execute
```

The atlas is written to:

```text
data/pixplot/met-cloud-200
```

Preview it locally from the project root:

```bash
node scripts/serve_pixplot.mjs
```

Then open:

```text
http://127.0.0.1:8771/data/pixplot/met-cloud-200/
```

The preview server must serve from the project root because PixPlot writes project-relative paths into its manifest. It also sends `content-length` headers because PixPlot's older loader uses those headers to calculate progress.
