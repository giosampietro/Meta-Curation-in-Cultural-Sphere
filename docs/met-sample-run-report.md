# Met Sample Run Report

Date: 2026-05-02

## Why We Ran This

The original project should be understood by touching a real archive, not only by reading its README. The Metropolitan Museum of Art scraper was chosen for the first test because it does not need an API key.

## Command In Plain Language

We asked the Met scraper:

- Search for the word `cloud`.
- Only process 2 object records.
- Save the results into a separate sample folder.

Technical command used:

```bash
python3 Methodology/01-data-collection\ /met_scraper.py --terms cloud --max 2 --output data/samples/met-cloud-test
```

## Result

The script worked.

- It found 278 Met records for `cloud`.
- It processed 2 object records.
- It downloaded 8 image files.
- It saved 2 metadata files.
- The sample folder is about 41 MB.

## Objects Collected

### 439844

- Title: Heroic Landscape with Rainbow
- Artist: Joseph Anton Koch
- Date: 1824
- Met URL: https://www.metmuseum.org/art/collection/search/439844
- Files:
  - `data/samples/met-cloud-test/images/439844.jpg`
  - `data/samples/met-cloud-test/images/439844_additional_1.jpg`
  - `data/samples/met-cloud-test/metadata/439844.json`

### 57416

- Title: Bowl decorated with cranes, rain, and chrysanthemums
- Artist: not listed in the sampled metadata
- Date: early 14th century
- Met URL: https://www.metmuseum.org/art/collection/search/57416
- Files:
  - `data/samples/met-cloud-test/images/57416.jpg`
  - `data/samples/met-cloud-test/images/57416_additional_1.jpg`
  - `data/samples/met-cloud-test/images/57416_additional_2.jpg`
  - `data/samples/met-cloud-test/images/57416_additional_3.jpg`
  - `data/samples/met-cloud-test/images/57416_additional_4.jpg`
  - `data/samples/met-cloud-test/images/57416_additional_5.jpg`
  - `data/samples/met-cloud-test/metadata/57416.json`

## What This Teaches Us

The original project has a real runnable seed: it can collect images and metadata from the Met.

It also has a usability problem. The `--max 2` setting means "process 2 object records," not "download exactly 2 images." One object can contain several additional images, so the result can be larger than expected.

For future interactive use, the browser interface should show this distinction clearly:

- object records
- primary images
- additional images
- estimated storage size

## Browser Review

A simple browser review page was created here:

- `data/samples/met-cloud-test/review.html`

This is not the future app. It is a tiny proof that image + metadata can be made understandable without asking you to inspect folders manually.
