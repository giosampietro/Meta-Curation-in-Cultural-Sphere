# PixPlot Integration Notes

PixPlot is the bridge between archive collection and visual interpretation.

## Project Meaning

In this project, PixPlot should not be treated as a neutral sorting machine. Its role is to create a spatial provocation: an image map where form, texture, color, and composition can suggest relationships that metadata search does not reveal.

The curator still has to interpret the map.

The correct workflow is:

1. Collect images and metadata.
2. Add subjective/manual images.
3. Generate a PixPlot map.
4. Look for clusters, outliers, echoes, and tensions.
5. Rename, split, merge, or reject machine groupings.
6. Use the result as material for a visual atlas or editorial sequence.

## Current Implementation

The repository now includes `scripts/run_pixplot.py`.

By default it:

- reads a collection folder
- writes `pixplot_metadata.csv`
- prints the PixPlot command that would run
- does not execute heavy machine-learning work unless `--execute` is passed

This is intentional. PixPlot has heavy pinned dependencies, including TensorFlow, and should be installed deliberately.

The repository also includes `docker/pixplot.Dockerfile`. This keeps the heavy PixPlot environment separate from the project files and from the main computer Python install.

## Current PixPlot Source Check

The current PixPlot README says to install from the Yale DHLab GitHub archive:

```bash
pip install https://github.com/yaledhlab/pix-plot/archive/master.zip
```

It then runs with:

```bash
pixplot --images "path/to/images/*.jpg" --metadata "path/to/metadata.csv"
```

The local integration follows that pattern.

## Metadata Mapping

The generated metadata CSV uses fields PixPlot understands:

- `filename`
- `category`
- `tags`
- `description`
- `permalink`
- `year`

For Met data:

- `category` comes from department.
- `tags` come from Met tag terms.
- `description` combines title, artist, and medium.
- `permalink` points back to the Met object record.
- `year` uses the object's begin date when available.

## Practical Constraint

The first larger working sample is `data/samples/met-cloud-200`.

Current sample status:

- 56 Met object records
- 211 image files
- 211 PixPlot metadata rows
- source keyword: `cloud`
- output target: `data/pixplot/met-cloud-200`

This is enough to start playing with PixPlot, but it is still a narrow collection. For stronger cultural interpretation, the next samples should mix sources, themes, and your own image archive.

## Docker PixPlot Workflow

Use Docker for PixPlot because the dependency stack is heavy and fragile.

Build the reusable local PixPlot image:

```bash
docker build -f docker/pixplot.Dockerfile -t metacuration-pixplot:local .
```

Run PixPlot against the 211-image sample:

```bash
docker run --rm -v "$PWD:/work" -w /work metacuration-pixplot:local python scripts/run_pixplot.py --collection data/samples/met-cloud-200 --execute
```

The important idea is simple: Docker holds PixPlot and TensorFlow; the Google Drive project folder holds the collection, metadata, and generated atlas.

## Local Preview

The generated PixPlot atlas should be served from the project root:

```bash
node scripts/serve_pixplot.mjs
```

Then open:

```text
http://127.0.0.1:8771/data/pixplot/met-cloud-200/
```

This matters because PixPlot writes project-relative paths in `data/manifest.json`. The preview server also sends `content-length` headers; without them, PixPlot's older loading screen can show `NaN%` and refuse to enter the map.

## Image Quality and Lazy Loading

PixPlot renders the zoomable map from atlas textures. Those are intentionally small so thousands of images can move smoothly in WebGL. Deep zoom can therefore look pixelated.

The project patch now improves the inspection modal instead of forcing every map tile to become high-resolution:

- PixPlot's own `data/originals` copies are often resized to about 600px tall.
- The collected source images in `data/samples/<collection>/images` are often larger.
- `assets/js/metacuration-highres.js` lazy-loads the larger source image only when an image is opened in the modal.
- This keeps the 5k map responsive while making clicked images clearer.

For sharper images directly inside the map, regenerate PixPlot with a larger `--cell-size`, for example `64`. That creates heavier atlas textures and may cost more memory/GPU performance. Use this only if map-level sharpness matters more than speed.

## Current Verification

Verified on May 2, 2026:

- PixPlot generated the full atlas for `met-cloud-200`.
- The browser preview opens to the WebGL map.
- The atlas loads with no browser console errors in the local preview.
- The map starts in UMAP layout with PixPlot's standard interactions.
- The serpent atlas modal lazy-loads higher-resolution images from `data/samples/serpents-open-5k/images`.

Docker note: the first one-off Docker run completed the atlas. Afterward Docker Desktop's command socket became slow/unresponsive for new `docker build` status calls, so the reusable Docker image is documented and ready but not yet confirmed as built locally.
