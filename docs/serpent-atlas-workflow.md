# Serpent Atlas Workflow

This is the first open-first implementation of the serpent atlas.

## What It Does

The serpent workflow collects image records from open/no-key museum APIs, normalizes the metadata, downloads web-sized images, and prepares review/PixPlot files.

Implemented sources:

- `met`: Metropolitan Museum of Art
- `vam`: Victoria and Albert Museum
- `aic`: Art Institute of Chicago
- `cma`: Cleveland Museum of Art

Planned but not yet implemented:

- `rijksmuseum`: needs a reliable image resolver for the newer Data Services endpoint
- `cooperhewitt`: needs careful GraphQL throttling because quick probes hit rate limiting
- Harvard, Europeana, Smithsonian: require API keys and are deferred

## Count-Only Probe

Use this before a larger scrape:

```bash
python3 scripts/collect_serpents.py --count-only --output data/samples/serpents-open-probe --sources met,vam,aic,cma --core-terms snake,serpent,serpenti
```

Verified counts for direct terms:

| Source | snake | serpent | serpenti |
|---|---:|---:|---:|
| Met | 1129 | 641 | 3 |
| V&A | 1408 | 921 | 1 |
| AIC | 99 | 129 | 0 |
| Cleveland | 114 | 154 | 0 |

## Current Working Runs

Small two-layer test:

```bash
python3 scripts/collect_serpents.py --output data/samples/serpents-open-two-layer-small --sources met,vam,aic,cma --core-terms snake,serpent --expanded-terms hydra,naga,Medusa,dragon --core-limit-per-term 2 --expanded-limit-per-term 2 --target-images 40
```

Result:

- 40 downloaded images
- sources: `aic`, `cma`, `met`, `vam`
- layers: `core`, `expanded`
- terms: `Medusa`, `dragon`, `hydra`, `naga`, `serpent`, `snake`

Core 300-image run:

```bash
python3 scripts/collect_serpents.py --output data/samples/serpents-open-core-300 --sources met,vam,aic,cma --core-terms snake,snakes,serpent,serpents,serpenti --core-limit-per-term 30 --target-images 300
```

Result:

- 300 downloaded images
- output size: about 204 MB
- source split: AIC 58, Cleveland 83, Met 97, V&A 62
- PixPlot metadata: `data/samples/serpents-open-core-300/pixplot_metadata.csv`

Serpent 5k atlas run:

```bash
python3 scripts/collect_serpents.py --output data/samples/serpents-open-5k --sources met,vam,aic,cma --core-terms snake,snakes,serpent,serpents,serpenti --expanded-terms hydra,naga,nagaraja,ouroboros,Medusa,Laocoon,Eden,"Saint George",Kaliya,Quetzalcoatl,Asclepius,dragon --core-limit-per-term 350 --expanded-limit-per-term 250 --target-images 5000
python3 scripts/collect_serpents.py --output data/samples/serpents-open-5k --sources vam,aic,cma --core-terms snake,snakes,serpent,serpents,serpenti --expanded-terms hydra,naga,nagaraja,ouroboros,Medusa,Laocoon,Eden,"Saint George",Kaliya,Quetzalcoatl,Asclepius,dragon --core-limit-per-term 600 --expanded-limit-per-term 600 --target-images 5000 --download-workers 8
```

Result:

- 5,307 downloaded image files
- collection size: about 1.4 GB
- clean PixPlot metadata: 5,307 rows and 5,307 unique filenames
- source split in PixPlot metadata: AIC 1,057; Cleveland 684; Met 201; V&A 3,365
- layer split in PixPlot metadata: core 1,835; expanded 3,472

## PixPlot Toggles

PixPlot metadata now includes:

- `source`
- `theme_layer`
- `search_term`
- `rights`

After PixPlot runs, `scripts/run_pixplot.py` automatically patches the generated atlas with `assets/js/metacuration-toggles.js`.

The toggles support:

- source filters
- layer filters
- search-term filters

If a toggle group is fully switched off, it resets to all-on to avoid a blank map.

## PixPlot Execution Status

PixPlot is running through Docker, not through the computer's system Python.

Docker was repaired on May 2, 2026 by force-stopping a wedged `com.docker.backend` process and reopening Docker Desktop. The low-level health check is:

```bash
curl --unix-socket /Users/giorgio/.docker/run/docker.sock http://localhost/_ping
```

Expected result:

```text
OK
```

The dry-run command for the 300-image collection is:

```bash
python3 scripts/run_pixplot.py --collection data/samples/serpents-open-core-300 --out-dir data/pixplot/serpents-open-core-300
```

Build the isolated PixPlot image:

```bash
docker build -f docker/pixplot.Dockerfile -t metacuration-pixplot:local .
```

Run the 5k serpent atlas:

```bash
docker run --rm -v "/Users/giorgio/Library/CloudStorage/GoogleDrive-gio@giosampietro.xyz/My Drive/01_Projects/Codex/ImageResearch/Meta-Curation-in-Cultural-Sphere:/work" -w /work metacuration-pixplot:local python scripts/run_pixplot.py --collection data/samples/serpents-open-5k --out-dir data/pixplot/serpents-open-5k --max-images 5000 --execute
```

Result:

- PixPlot processed 5,306 images after skipping one oblong image.
- Output atlas: `data/pixplot/serpents-open-5k`
- Output size: about 376 MB
- Source/layer/search-term toggles were patched into the generated atlas.

Preview URL:

```text
http://127.0.0.1:8771/data/pixplot/serpents-open-5k/
```
