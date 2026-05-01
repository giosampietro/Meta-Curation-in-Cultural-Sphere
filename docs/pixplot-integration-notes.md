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

The current sample has only 8 images. That is enough to test plumbing, not enough for meaningful clustering. For real cultural interpretation, use a larger mixed collection.
