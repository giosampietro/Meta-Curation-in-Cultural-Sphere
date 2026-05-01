# Original-First Walkthrough

This document explains the project in human terms before we change it.

## What The Project Is Trying To Do

The project proposes a hybrid curation method for cultural image collections. It starts from institutional databases, but it does not accept metadata search as the final truth. Instead, it treats archive APIs, museum categories, search terms, and visual clustering as cultural systems that can be questioned and reinterpreted.

The theme in the repository is "cloud." The important move is that "cloud" is not only a keyword. It becomes a visual and cultural condition: vapor, softness, drift, atmosphere, wool, foam, smoke, lightness, ambiguity.

## The Four Phases

### 1. Automated Data Collection

This phase uses museum and cultural archive APIs to search for images and metadata. The repo includes individual Python scrapers for:

- Metropolitan Museum of Art
- Harvard Art Museums
- Europeana
- Cooper Hewitt
- Smithsonian

The scripts are real code, but they are separate prototypes. The README describes a unified command like `python scripts/collect_images.py`, but that file does not exist in the repo.

### 2. Subjective Archive Mixing

This is where the project becomes culturally interesting. After API collection, a human curator adds images that are "cloud-like" without necessarily being literal clouds.

The repository connects this to Aby Warburg's Mnemosyne Atlas: meaning is built through juxtaposition, resonance, visual memory, and spatial arrangement rather than only through chronology or metadata.

### 3. Visual Clustering

The project proposes PixPlot as the clustering tool. PixPlot places images on a two-dimensional map based on visual similarity: color, form, texture, composition, and related visual features.

In the current repo, this phase is documentation only. The README mentions PixPlot setup files and helper scripts, but those files are not present.

### 4. Editorial Workflow

The final phase translates clusters into page-by-page editorial planning. The docs describe Excel templates, page assignments, InDesign exports, captions, and layout validation.

This is also documentation only in the current repo. The editorial README appears to end mid-sentence, which suggests it is unfinished.

## What Is Actually Present

Tracked files in the cloned repo:

- `README.md`
- `CONTRIBUTING.md`
- `Methodology/01-data-collection  /data-collection-README.md`
- `Methodology/01-data-collection /met_scraper.py`
- `Methodology/01-data-collection /harvard_scraper.py`
- `Methodology/01-data-collection /europeana_scraper.py`
- `Methodology/01-data-collection /cooper_hewitt_scraper.py`
- `Methodology/01-data-collection /smithsonian-cloud-scraper.py`
- `Methodology/02-mixing-archive/README.md`
- `Methodology/02-mixing-archive/warburg_inspiration.md`
- `Methodology/03-visual-clustering /visual-clustering-README.md`
- `Methodology/04- editorial-workflow / editorial-workflow-README.md`

## What Is Described But Missing

The current README or methodology documents refer to these missing project pieces:

- `requirements.txt`
- `config/api_keys.json.template`
- `config/api_keys.json`
- `config/api_config.yaml`
- `data_sources/api_endpoints.json`
- `scripts/collect_images.py`
- `scripts/pixplot_integration.py`
- `scripts/run_collection.py`
- `scripts/validate_downloads.py`
- `scripts/generate_metadata_report.py`
- PixPlot setup/config folders
- Recuration helper tools
- Editorial export helper tools
- Excel and InDesign templates

This means the project is closer to a methodology plus prototype scripts than a complete working application.

## What Can Run First

The best first test is the Met scraper:

- It uses the public Met API.
- It does not require an API key.
- It can download images and metadata.
- It can be run at a very small scale.

The other scrapers should wait until we add proper API key handling and repair obvious issues.

## How To Think About The Next Evolution

The future app should preserve three layers:

- Cultural method: the theory of archive, metadata, subjectivity, and juxtaposition.
- Technical pipeline: import, metadata, image processing, clustering, review, export.
- Living atlas: a private visual workspace where you can curate, annotate, override, and publish selected constellations.
