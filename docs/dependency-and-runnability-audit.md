# Dependency And Runnability Audit

This document records what is needed to run the current repository.

## Current Runtime

Local Python version checked during audit:

- Python 3.9.4

Python syntax check:

- `met_scraper.py`: OK
- `harvard_scraper.py`: OK
- `europeana_scraper.py`: OK
- `cooper_hewitt_scraper.py`: OK
- `smithsonian-cloud-scraper.py`: OK

Syntax OK means the files can be parsed as Python. It does not mean each script behaves correctly.

## Installed Or Missing Packages

Observed imports:

- Standard Python libraries: `os`, `json`, `time`, `argparse`, `random`, `datetime`, `pathlib`, `urllib.parse`, `concurrent.futures`
- External package: `requests`
- External package: `python-dotenv` imported as `dotenv`

Current local package availability:

- `requests`: installed
- `dotenv`: missing

There is no `requirements.txt`, so dependencies are not documented in a machine-installable way.

Update: Phase 2 added `requirements.txt` for baseline scraper dependencies and `requirements-pixplot.txt` for optional PixPlot installation.

## Script-By-Script Notes

### Met Scraper

File: `Methodology/01-data-collection /met_scraper.py`

Status: best first candidate.

Why:

- No API key required.
- Has command-line options for search terms, exclusions, max results, and output folder.
- Creates image and metadata folders.

Risk:

- The `--max` value limits object IDs per search term, but each object can include additional images.
- It uses multiple workers, so it can make several requests at once.

### Harvard Scraper

File: `Methodology/01-data-collection /harvard_scraper.py`

Status: needs repair before normal use.

Why:

- Requires Harvard Art Museums API key.
- Defines a `main()` function but does not call it at the end.

### Europeana Scraper

File: `Methodology/01-data-collection /europeana_scraper.py`

Status: needs API key and review.

Why:

- Requires Europeana API key.
- Contains an unused `async def download_image` method, while the active code downloads synchronously.

### Cooper Hewitt Scraper

File: `Methodology/01-data-collection /cooper_hewitt_scraper.py`

Status: not safe to run as-is.

Why:

- Requires Cooper Hewitt API key.
- Hardcodes `YOUR_API_KEY_HERE`.
- At the bottom, it tries to create `HarvardArtScraper(API_KEY)`, but `HarvardArtScraper` is not defined in this file.

### Smithsonian Scraper

File: `Methodology/01-data-collection /smithsonian-cloud-scraper.py`

Status: needs API key and dependency.

Why:

- Requires `SMITHSONIAN_API_KEY`.
- Imports `dotenv`, but `python-dotenv` is not currently installed.
- Creates output directories immediately when imported or run.

## Missing Project Infrastructure

The repo currently lacks:

- Output schema validator
- Interactive review interface

Update: Phase 2 added a dependency file, API key template, Met-only collection command, PixPlot runner, review generator, and tests. The interactive review interface is still only a generated HTML page, not a full app.

## First Safe Run

Use the Met scraper with a very small limit and a separate output folder. This keeps the test understandable and reversible.

Expected output:

- `data/samples/met-cloud-test/images/`
- `data/samples/met-cloud-test/metadata/`

The sample should answer a simple question: can the original project collect real images and metadata from at least one no-key archive?

## First Safe Run Result

Status: successful.

The Met scraper was run with the search term `cloud`, a max setting of 2 object records, and a separate output folder.

Result:

- 278 matching Met object records found.
- 2 object records processed.
- 8 image files downloaded.
- 2 metadata files saved.
- Output size: about 41 MB.

The browser review page is:

- `data/samples/met-cloud-test/review.html`

Important lesson: in this script, `--max` limits object records, not total image files. The browser version should make that distinction clear before running a collection.

## PixPlot Readiness

PixPlot is not installed locally. The bridge script can still prepare metadata and print the exact command.

Current bridge:

```bash
python3 scripts/run_pixplot.py --collection data/samples/met-cloud-test
```

Optional install path:

```bash
python3 -m pip install -r requirements-pixplot.txt
```

This should be treated carefully because PixPlot depends on a large machine-learning stack.
