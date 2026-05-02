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

PixPlot execution is prepared but currently blocked by local Docker Desktop's command socket hanging on `docker ps`.

The dry-run command for the 300-image collection is:

```bash
python3 scripts/run_pixplot.py --collection data/samples/serpents-open-core-300 --out-dir data/pixplot/serpents-open-core-300
```

When Docker is responsive again, the isolated PixPlot run should use:

```bash
docker build -f docker/pixplot.Dockerfile -t metacuration-pixplot:local .
docker run --rm -v "$PWD:/work" -w /work metacuration-pixplot:local python scripts/run_pixplot.py --collection data/samples/serpents-open-core-300 --out-dir data/pixplot/serpents-open-core-300 --execute
```
