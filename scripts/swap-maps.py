#!/usr/bin/env python3
"""Replace inline SVG maps with image-based maps across the 5 wood pages.

Swaps the <svg viewBox="0 0 600 420">...</svg> block for an <img> tag, and
converts the numbered legend (<ol> with .n badges) to a clean <ul> with
bolded feature names.
"""

import re
from pathlib import Path

WOODS = {
    "sussex.html": (
        "map-sussex.jpg",
        "A hand-painted illustrated map of the Hundred Acre Wood — the "
        "warden's lodge, the dell with rope bridges, the bee tree, the "
        "North Pole stump, and Eeyore's Field — on aged cream paper",
    ),
    "dordogne.html": (
        "map-dordogne.jpg",
        "A hand-painted illustrated map of Le Bois de Cent Acres — the "
        "pilgrim path, the chestnut grove, the walnut stand, the beehive, "
        "and the river — on aged cream paper",
    ),
    "andalusia.html": (
        "map-andalusia.jpg",
        "A hand-painted illustrated map of El Bosque de las Cien Acres — "
        "the cork grove, the umbrella-pine ridge, the harvest track, the "
        "lynx stones, and the cork hut — on aged cream paper",
    ),
    "tuscany.html": (
        "map-tuscany.jpg",
        "A hand-painted illustrated map of Il Bosco dei Cento Acri — the "
        "ruined chapel, the pilgrim path, the cypress lane, the holm oak "
        "stand, and the Bellini stone — on aged cream paper",
    ),
    "krasnodar.html": (
        "map-krasnodar.jpg",
        "A hand-painted illustrated map of Сто-Акровый Лес — the beech "
        "avenue, the silver fir crest, the bear stream, the warden's "
        "lodge, and the wartime memorial — on aged cream paper",
    ),
}

BASE = Path(__file__).resolve().parent.parent / "public"

svg_re = re.compile(r"<svg viewBox=\"0 0 600 420\".*?</svg>", re.DOTALL)
legend_item_re = re.compile(
    r"<li><span class=\"n\">\d+</span><span>([^—]+) —\s*([^<]+)</span></li>"
)


def transform(text: str, mapfile: str, alt: str) -> str:
    # Replace SVG with image
    new_img = (
        f'<img src="/img/{mapfile}" alt="{alt}" loading="lazy">'
    )
    text, n_svg = svg_re.subn(new_img, text, count=1)
    if n_svg != 1:
        raise SystemExit(f"  ✗ SVG not found / not unique")

    # ol → ul (only the legend ol; wood pages only have this one)
    text = text.replace("<ol>\n            ", "<ul>\n            ", 1)
    text = text.replace("          </ol>", "          </ul>", 1)

    # Strip numbered badges; convert each <li> to <li><strong>Name</strong> — desc.</li>
    text, n_li = legend_item_re.subn(
        lambda m: f"<li><strong>{m.group(1).strip()}</strong> — {m.group(2).strip()}</li>",
        text,
    )

    # Slight copy tweak: "Marked features" → "In this wood"
    text = text.replace(">Marked features<", ">In this wood<")

    return text, n_li


for fname, (mapfile, alt) in WOODS.items():
    path = BASE / fname
    src = path.read_text(encoding="utf-8")
    out, n_items = transform(src, mapfile, alt)
    path.write_text(out, encoding="utf-8")
    print(f"  ✓ {fname:18s}  ({n_items} legend items)")

print("done.")
