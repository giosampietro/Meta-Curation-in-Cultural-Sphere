from __future__ import annotations

from pathlib import Path


TOGGLE_SCRIPT = r"""(() => {
  const GROUPS = [
    { key: "source", label: "Sources" },
    { key: "theme_layer", label: "Layers" },
    { key: "search_term", label: "Terms" },
  ];
  const state = {};
  let metadataByImage = {};

  function waitForPixplot() {
    return new Promise((resolve) => {
      const tick = () => {
        if (window.data && window.world && data.json && Array.isArray(data.json.images)) resolve();
        else window.setTimeout(tick, 250);
      };
      tick();
    });
  }

  async function loadMetadata() {
    const pairs = await Promise.all(data.json.images.map(async (filename) => {
      try {
        const response = await fetch(`data/metadata/file/${filename}.json`);
        return [filename, await response.json()];
      } catch {
        return [filename, { filename }];
      }
    }));
    metadataByImage = Object.fromEntries(pairs);
  }

  function valuesFor(key) {
    return [...new Set(Object.values(metadataByImage).map((row) => row[key]).filter(Boolean))].sort();
  }

  function activeValues(key) {
    return state[key] || new Set(valuesFor(key));
  }

  function resetGroupIfEmpty(key, values) {
    if (activeValues(key).size > 0) return;
    state[key] = new Set(values);
    document.querySelectorAll(`[data-metacuration-key="${key}"] input`).forEach((input) => {
      input.checked = true;
    });
  }

  function imageVisible(row) {
    return GROUPS.every((group) => {
      const value = row[group.key];
      const active = activeValues(group.key);
      return !value || active.has(value);
    });
  }

  function applyFilters() {
    const indices = [];
    data.json.images.forEach((filename, idx) => {
      if (imageVisible(metadataByImage[filename] || {})) indices.push(idx);
    });
    world.setOpaqueImages(indices);
  }

  function buildGroup(group) {
    const values = valuesFor(group.key);
    if (values.length < 2) return "";
    state[group.key] = new Set(values);
    return `<fieldset class="metacuration-toggle-group" data-metacuration-key="${group.key}">
      <legend>${group.label}</legend>
      ${values.map((value) => `<label><input type="checkbox" checked value="${value}"><span>${value}</span></label>`).join("")}
    </fieldset>`;
  }

  function buildControls() {
    const panel = document.createElement("aside");
    panel.id = "metacuration-toggles";
    panel.innerHTML = `<div class="metacuration-toggle-title">Atlas Filters</div>${GROUPS.map(buildGroup).join("")}`;
    document.body.appendChild(panel);
    panel.addEventListener("change", (event) => {
      const input = event.target;
      if (!input.matches("input[type='checkbox']")) return;
      const group = input.closest("[data-metacuration-key]");
      const key = group.getAttribute("data-metacuration-key");
      const values = valuesFor(key);
      const next = new Set([...group.querySelectorAll("input:checked")].map((node) => node.value));
      state[key] = next;
      resetGroupIfEmpty(key, values);
      applyFilters();
    });
  }

  function injectStyles() {
    const style = document.createElement("style");
    style.textContent = `
      #metacuration-toggles {
        position: fixed;
        left: 16px;
        top: 64px;
        z-index: 20;
        max-width: min(320px, calc(100vw - 32px));
        max-height: calc(100vh - 96px);
        overflow: auto;
        color: #f4f1ea;
        background: rgba(18, 18, 18, 0.86);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 12px;
        font-family: Inter, system-ui, sans-serif;
      }
      .metacuration-toggle-title { font-weight: 700; margin: 0 0 8px; }
      .metacuration-toggle-group { border: 0; margin: 0 0 10px; padding: 0; }
      .metacuration-toggle-group legend { color: #d8c58a; font-size: 12px; margin-bottom: 6px; text-transform: uppercase; }
      .metacuration-toggle-group label { display: inline-flex; align-items: center; gap: 5px; margin: 0 8px 8px 0; font-size: 12px; }
    `;
    document.head.appendChild(style);
  }

  waitForPixplot().then(loadMetadata).then(() => {
    injectStyles();
    buildControls();
    applyFilters();
  });
})();
"""


HIGH_RES_SCRIPT = r"""(() => {
  const SOURCE_COLLECTION = "__SOURCE_COLLECTION__";

  function filenameFromPixplotSrc(src) {
    const match = String(src || "").match(/\/originals\/([^?#]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function upgradeSelectedImage() {
    const image = document.querySelector("#selected-image");
    if (!image || image.dataset.metacurationHighres === "true") return;
    const filename = filenameFromPixplotSrc(image.getAttribute("src"));
    if (!filename) return;
    const highres = `${SOURCE_COLLECTION}/${encodeURIComponent(filename)}`;
    image.dataset.metacurationHighres = "true";
    image.dataset.pixplotSrc = image.getAttribute("src");
    image.decoding = "async";
    image.loading = "eager";
    image.src = highres;
    document.querySelector("#download-icon")?.setAttribute("href", highres);
  }

  function injectStyles() {
    const style = document.createElement("style");
    style.textContent = `
      #selected-image {
        image-rendering: auto;
      }
      #selected-image-container::after {
        content: "High-res image loaded on open";
        position: absolute;
        right: 14px;
        bottom: 14px;
        padding: 5px 7px;
        color: rgba(255, 255, 255, 0.86);
        background: rgba(0, 0, 0, 0.52);
        font: 11px/1.2 Open Sans, system-ui, sans-serif;
        pointer-events: none;
      }
    `;
    document.head.appendChild(style);
  }

  injectStyles();
  new MutationObserver(upgradeSelectedImage).observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["src"],
  });
})();
"""


def patch_pixplot_toggles(atlas_dir: Path) -> None:
    atlas_dir = Path(atlas_dir)
    index_path = atlas_dir / "index.html"
    assets_dir = atlas_dir / "assets" / "js"
    script_path = assets_dir / "metacuration-toggles.js"
    high_res_path = assets_dir / "metacuration-highres.js"
    assets_dir.mkdir(parents=True, exist_ok=True)
    script_path.write_text(TOGGLE_SCRIPT, encoding="utf-8")
    source_collection = f"/data/samples/{atlas_dir.name}/images"
    high_res_path.write_text(
        HIGH_RES_SCRIPT.replace("__SOURCE_COLLECTION__", source_collection),
        encoding="utf-8",
    )

    index = index_path.read_text(encoding="utf-8")
    tags = [
        "    <script src='assets/js/metacuration-toggles.js'></script>",
        "    <script src='assets/js/metacuration-highres.js'></script>",
    ]
    changed = False
    for tag in tags:
        script_name = tag.split("assets/js/", 1)[1].split(".js", 1)[0] + ".js"
        if script_name in index:
            continue
        if "</body>" in index:
            index = index.replace("</body>", f"{tag}\n  </body>")
        else:
            index = f"{index}\n{tag}\n"
        changed = True
    if changed:
        index_path.write_text(index, encoding="utf-8")
