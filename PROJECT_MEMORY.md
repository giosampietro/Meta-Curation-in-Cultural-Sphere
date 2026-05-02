# Project Memory: Meta-Curation in Cultural Sphere

Last updated: 2026-05-02

## What This Copy Is

This folder is your forked copy of HuiBaqueroVall's `Meta-Curation-in-Cultural-Sphere` project.

- Your fork: https://github.com/giosampietro/Meta-Curation-in-Cultural-Sphere
- Original upstream: https://github.com/HuiBaqueroVall/Meta-Curation-in-Cultural-Sphere
- Local folder: `/Users/giorgio/Library/CloudStorage/GoogleDrive-gio@giosampietro.xyz/My Drive/01_Projects/Codex/ImageResearch/Meta-Curation-in-Cultural-Sphere`

We are treating the original project first as an object of study, not as raw material to overwrite. The immediate goal is understanding: what the project argues culturally, what code exists, what is missing, and what needs repair before the work can become interactive.

## Plain-Language Summary

The project is about digital archives as systems that shape what becomes visible. Its core claim is that museum databases and image archives do not simply "contain" culture. They organize it through metadata, APIs, search terms, categories, and institutional priorities.

The proposed method has four movements:

1. Collect images from institutional archives using search terms and APIs.
2. Add subjective, intuitive images that expand the theme beyond literal search results.
3. Cluster the mixed image set visually, so form and atmosphere can produce new taxonomies.
4. Turn the clusters into editorial sequences or layouts.

The cultural heart is strong. The software is not yet a complete app.

## What We Have Done

- Confirmed GitHub access as `giosampietro`.
- Forked the original repository into your GitHub account.
- Cloned your fork locally.
- Verified remotes:
  - `origin` is your fork.
  - `upstream` is the original repository.
- Audited the file structure.
- Confirmed the repo has 12 tracked files.
- Confirmed there is no formal `LICENSE` file in the cloned repo.
- Confirmed there is no `requirements.txt`, even though the README references one.
- Confirmed the Python files are syntactically valid Python.
- Ran a small Met API sample for the search term `cloud`.
- Created a simple browser review page for the sample output.
- Started Phase 2 on branch `phase-2-runnable-met-pixplot`.
- Added a tested Met-only runner that wraps the original Met scraper.
- Added a tested review/metadata generator.
- Added a PixPlot bridge that prepares metadata and prints or runs the PixPlot command.
- Downloaded a larger Met sample for the search term `cloud`.
- Ran PixPlot successfully on that larger sample.
- Added a local PixPlot preview server.

## Important Findings

- The README describes a more complete project than the repository currently contains.
- Several folders have trailing spaces in their names, which makes paths awkward and fragile.
- The Met scraper is the best first runnable candidate because the Met API does not require an API key.
- Harvard, Europeana, Cooper Hewitt, and Smithsonian scripts require API keys or environment setup.
- The PixPlot and editorial workflow sections are mostly documentation; the scripts they mention are not present.
- `harvard_scraper.py` defines a `main()` function but does not call it at the bottom.
- `cooper_hewitt_scraper.py` tries to call `HarvardArtScraper`, which is not defined in that file.
- `editorial-workflow-README.md` appears to end mid-thought.
- The first Met sample found 278 object records, processed 2 object records, downloaded 8 image files, and produced 2 metadata files.
- A `--max 2` Met run does not mean "download exactly 2 images." It means "process 2 object records," and each object may include additional images.
- PixPlot is not installed directly on the computer. It has been run through Docker once, and the repo now has a Dockerfile for future isolated runs.
- Docker generated the first full PixPlot atlas, but Docker Desktop's command socket became slow/unresponsive afterward when trying to build the reusable image. The Dockerfile is ready; the image build still needs a clean Docker retry.

## Current Working Sample

As of May 2, 2026, the first larger sample is working locally:

- Collection: `data/samples/met-cloud-200`
- Source: The Met API
- Keyword: `cloud`
- Object records: 56
- Image files: 211
- Review page: `data/samples/met-cloud-200/review.html`
- PixPlot metadata: `data/samples/met-cloud-200/pixplot_metadata.csv`
- PixPlot atlas: `data/pixplot/met-cloud-200`
- Local preview command: `node scripts/serve_pixplot.mjs`
- Local preview URL: `http://127.0.0.1:8771/data/pixplot/met-cloud-200/`

The atlas has been browser-verified and opens into the WebGL map.

## Working Rule

Preserve the original project while we understand it. Any future repair should be small, documented, and reversible.

The first evolution path is:

1. Read-first walkthrough.
2. Small no-key Met test.
3. Minimal repairs to make the original runnable.
4. Browser-based interaction so you do not need terminal or file handling.
5. Later: custom living atlas with Google Drive, Vertex AI, Cloudflare, and publishable views.

## Useful Files Created In This Fork

- `docs/original-first-walkthrough.md`
- `docs/dependency-and-runnability-audit.md`
- `docs/nontechnical-project-map.md`
- `docs/met-sample-run-report.md`
- `docs/phase-2-runnable-workflow.md`
- `docs/pixplot-integration-notes.md`
- `data/samples/met-cloud-test/review.html`
- `scripts/serve_pixplot.mjs`
- `docker/pixplot.Dockerfile`

## Current Runnable Commands

Small Met collection:

```bash
python3 scripts/collect_images.py --keyword cloud --limit 2 --output data/samples/met-cloud-test
```

PixPlot preparation dry run:

```bash
python3 scripts/run_pixplot.py --collection data/samples/met-cloud-test
```

Preview the current PixPlot atlas:

```bash
node scripts/serve_pixplot.mjs
```

Then open:

```text
http://127.0.0.1:8771/data/pixplot/met-cloud-200/
```
