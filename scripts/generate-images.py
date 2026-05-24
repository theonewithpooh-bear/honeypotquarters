#!/usr/bin/env python3
"""Generate photographic and illustrative imagery for honeypotquarters.com.

Uses gpt-image-2 via the OpenAI API. Reads OPENAI_API_KEY from the environment.
Saves PNGs into ../public/img/. Skips any image whose output file already exists
unless --force is passed.

Usage:
    OPENAI_API_KEY=sk-... .venv/bin/python scripts/generate-images.py [--force]
"""

import argparse
import base64
import sys
import time
from pathlib import Path

from openai import OpenAI

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "img"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Image set. Prompts written for a "casual phone snapshot" aesthetic:
#  - candid / unposed / honest framing
#  - subtle phone-camera grain, natural color balance
#  - no people, no signs, no overpolish
# -----------------------------------------------------------------------------

PHONE_PHOTO_TAIL = (
    " Honest unposed framing, slight handheld tilt, taken on an iPhone at chest "
    "height by a casual walker. Natural color balance, subtle phone-camera grain, "
    "no glamorization, no heavy retouching, no people, no signs, no human-made "
    "infrastructure beyond what the prompt describes. Slight softness as if walking."
)

IMAGES = [
    # ---- HOMEPAGE HERO ------------------------------------------------------
    {
        "filename": "home-hero.png",
        "size": "1536x1024",
        "prompt": (
            "Candid amateur landscape photograph: a narrow grass path leading into a "
            "dense English deciduous woodland in late May, golden hour, dappled "
            "afternoon sun through fresh hornbeam and oak leaves, the path is faint "
            "and unmade, fallen branches at the edges, no signs, no fence, no people."
            + PHONE_PHOTO_TAIL
        ),
    },
    # ---- SUSSEX -------------------------------------------------------------
    {
        "filename": "wood-sussex.png",
        "size": "1536x1024",
        "prompt": (
            "Candid iPhone photograph of an English woodland in late May: ancient "
            "hornbeam and oak trees with mossy trunks, a soft layer of bluebell "
            "stems going over, gentle afternoon light filtering through fresh "
            "leaves, a faint deer path winding into the middle distance."
            + PHONE_PHOTO_TAIL
        ),
    },
    # ---- DORDOGNE -----------------------------------------------------------
    {
        "filename": "wood-dordogne.png",
        "size": "1536x1024",
        "prompt": (
            "Casual iPhone snapshot of a French chestnut and walnut wood in early "
            "summer, Dordogne region: dappled mid-morning light, a narrow pale "
            "limestone path crossing the frame, low moss-covered dry-stone walls, "
            "sweet chestnut leaves in fresh bright green, dust hanging in the air "
            "above the path, slightly tilted horizon as if the photographer didn't "
            "bother to straighten it." + PHONE_PHOTO_TAIL
        ),
    },
    # ---- ANDALUSIA ----------------------------------------------------------
    {
        "filename": "wood-andalusia.png",
        "size": "1536x1024",
        "prompt": (
            "Casual iPhone photograph of a sun-baked Andalucían hillside in late "
            "spring, Sierra de Aracena: cork oak trees with their lower trunks "
            "stripped to bare orange-red wood from harvest (a normal sight in the "
            "region), umbrella pines in the background, dry pale grass turning "
            "gold, warm hazy afternoon sun, dust haze in the air, slightly "
            "overexposed by the bright sun." + PHONE_PHOTO_TAIL
        ),
    },
    # ---- TUSCANY ------------------------------------------------------------
    {
        "filename": "wood-tuscany.png",
        "size": "1536x1024",
        "prompt": (
            "Casual iPhone photograph in a Val d'Orcia woodland at low evening "
            "light: holm oak and umbrella pine trees, in the middle ground the "
            "ruined stone walls of a small 14th-century chapel — only one wall "
            "fully standing, the rest collapsed and overgrown with grass and "
            "brambles, no roof, weathered stone, warm Italian golden hour."
            + PHONE_PHOTO_TAIL
        ),
    },
    # ---- KRASNODAR ----------------------------------------------------------
    {
        "filename": "wood-krasnodar.png",
        "size": "1536x1024",
        "prompt": (
            "Casual iPhone photograph of a Caucasian beech and silver fir forest on "
            "a mountain slope in early summer, western Caucasus: tall straight pale "
            "beech trunks, dark silver fir in the background, a mossy fallen log "
            "across the foreground, soft cool overcast light, mist between distant "
            "trees, damp atmosphere, cool tones." + PHONE_PHOTO_TAIL
        ),
    },
    # ---- ATLAS ATMOSPHERIC --------------------------------------------------
    {
        "filename": "atlas-detail.png",
        "size": "1024x1024",
        "prompt": (
            "Casual overhead iPhone photograph of an open antique European atlas "
            "page on a wooden desk: yellowed paper, copperplate engraved map of "
            "western Europe, hand-tinted in pale watercolor washes, a brass "
            "compass paperweight resting on one corner, a single dried oak leaf "
            "laid across the page, warm afternoon window light from the left, "
            "honest unposed snapshot, slight glare on the paper, shadow of the "
            "phone faintly visible, natural color balance, subtle grain. "
            "Photographed at desk height, looking down, slightly off-center."
        ),
    },
    # ---- WAX SEAL -----------------------------------------------------------
    {
        "filename": "wax-seal.png",
        "size": "1024x1024",
        "prompt": (
            "Macro iPhone photograph of a deep amber-gold wax seal pressed onto a "
            "creased cream parchment letter: the seal shows a six-sided honeycomb "
            "cell pattern with a small bee at its centre, the wax has cooled "
            "unevenly with visible texture and a small crack, the parchment shows "
            "faint horizontal folds and slight foxing at the edges, soft natural "
            "window light from the upper left, no other objects in frame, "
            "completely honest amateur close-up snapshot, subtle phone-camera "
            "grain, natural color balance, no studio polish."
        ),
    },
]

# -----------------------------------------------------------------------------
# Illustrated map images. Hand-painted watercolor + brown ink on aged cream
# paper, top-down view of a small wood, hand-lettered labels. Photographed
# slightly tilted on a wooden surface in natural window light — as if the
# warden's map were lying on a desk.
# -----------------------------------------------------------------------------

MAP_STYLE = (
    " Hand-painted illustrated estate map, top-down view on aged cream paper "
    "with slightly foxed edges. Watercolor washes over fine brown ink linework. "
    "Schematic tiny tree icons (little ink trees), dashed brown ink paths, tiny "
    "ink buildings. A compass rose in one corner. A scale bar reading '100 acres'. "
    "Hand-lettered serif labels in irregular print. The style of a small private "
    "trust's warden's map — beautiful but unfussy, drawn by hand. "
    "Photographed slightly tilted on a wooden table in soft natural window "
    "light, like a casual phone snapshot of the map, with paper texture and a "
    "faint shadow at one edge. No people, no modern elements, no GPS markings."
)

MAPS = [
    # ---- EUROPE (homepage) --------------------------------------------------
    {
        "filename": "map-europe.png",
        "size": "1536x1024",
        "prompt": (
            "An antique-style illustrated wall map of Europe on aged cream paper, "
            "with five woodland properties marked by small honey-gold circular "
            "pins, each labelled by hand: 'I. Sussex' in southern England, "
            "'II. Dordogne' in southwest France, 'III. Andalusia' in southern "
            "Spain, 'IV. Tuscany' in central Italy, and 'V. Krasnodar' in the "
            "western Caucasus of Russia. Watercolor wash of pale green for land, "
            "pale blue for sea, with hand-drawn brown ink coastlines, dashed sea "
            "grid lines, and tiny illustrated cartouche reading 'THE FIVE WOODS "
            "OF HONEYPOT QUARTERS' in hand-lettered serif. A large compass rose "
            "in the lower-right corner with N, S, E, W marked. Slight foxing on "
            "the paper edges. The style of a small private trust's antique-feel "
            "wall map. Photographed slightly tilted in natural window light, like "
            "a casual phone snapshot of the map lying on a wooden lectern, with "
            "paper texture visible. No modern elements, no people."
        ),
    },
    # ---- SUSSEX -------------------------------------------------------------
    {
        "filename": "map-sussex.png",
        "size": "1536x1024",
        "prompt": (
            "An illustrated estate map of an English wood titled 'THE HUNDRED ACRE "
            "WOOD' in large hand-lettered serif at the top, subtitled 'Sussex · "
            "surveyed Oct. MMXXIV'. The wood is roughly oval with an irregular "
            "boundary. Features shown and labelled by hand: a tiny wardens' lodge "
            "(small house icon) at the south boundary, a central sunken dell with "
            "three rope bridges (zigzag rope lines) crossing it, a large hornbeam "
            "tree on the west side labelled 'BEE TREE' with small bees drawn "
            "around it, a tree stump on the north boundary labelled 'NORTH POLE', "
            "and a small east meadow labelled 'EEYORE'S FIELD'. Pale sage-green "
            "watercolor wash over the wooded area. Dashed brown ink paths "
            "connecting features." + MAP_STYLE
        ),
    },
    # ---- DORDOGNE -----------------------------------------------------------
    {
        "filename": "map-dordogne.png",
        "size": "1536x1024",
        "prompt": (
            "An illustrated estate map of a French wood titled 'LE BOIS DE CENT "
            "ACRES' in large hand-lettered serif at the top, subtitled 'Dordogne "
            "· relevé automne MMXXIV'. The wood is irregularly shaped. Features "
            "shown and labelled by hand: a pale limestone pilgrim path crossing "
            "the wood east-to-west (drawn as a wider double line) labelled 'LE "
            "SENTIER DU PÈLERIN', a cluster of small chestnut trees in the "
            "northwest labelled 'LES CHÂTAIGNIERS', a smaller cluster of walnut "
            "trees on the south side labelled 'NOYERS', a single beehive at the "
            "northern bend of the path labelled 'LA RUCHE', a partly-collapsed "
            "dry-stone wall labelled 'LE MUR', and a small river along the "
            "southern boundary (drawn in pale blue) labelled 'LA RIVIÈRE'. Pale "
            "warm sandstone-brown watercolor wash over the wooded area." + MAP_STYLE
        ),
    },
    # ---- ANDALUSIA ----------------------------------------------------------
    {
        "filename": "map-andalusia.png",
        "size": "1536x1024",
        "prompt": (
            "An illustrated estate map of a Spanish wood titled 'EL BOSQUE DE LAS "
            "CIEN ACRES' in large hand-lettered serif at the top, subtitled "
            "'Andalucía · levantado otoño MMXXIV'. The wood sits on sloped "
            "hillside, with hand-drawn brown ink contour lines suggesting the "
            "slope. Features shown and labelled by hand: a cluster of cork oak "
            "trees in the southern half (drawn with their characteristic stripped "
            "orange-red lower trunks) labelled 'EL ALCORNOCAL', a row of "
            "umbrella pines (distinctive flat-topped canopy) along the upper "
            "ridge labelled 'LOS PINOS', a dashed cart track winding through the "
            "cork grove labelled 'EL CARRIL DE LA SACA', a small dry stream "
            "labelled 'EL ARROYO' running north-south, three small boulders "
            "labelled 'LAS PIEDRAS DEL LINCE' (the lynx stones), and a tiny "
            "stone hut on the eastern side labelled 'EL CASTAÑUELO'. Pale ochre "
            "and warm tan watercolor wash for the dry hillside, sage-green for "
            "the pine ridge." + MAP_STYLE
        ),
    },
    # ---- TUSCANY ------------------------------------------------------------
    {
        "filename": "map-tuscany.png",
        "size": "1536x1024",
        "prompt": (
            "An illustrated estate map of an Italian wood titled 'IL BOSCO DEI "
            "CENTO ACRI' in large hand-lettered serif at the top, subtitled "
            "'Toscana · rilevato autunno MMXXIV'. Features shown and labelled by "
            "hand: at the very centre of the wood, the small footprint of a "
            "ruined 14th-century chapel — only its north wall partly standing, "
            "the rest shown as collapsed stones — labelled 'LA CAPPELLA "
            "(rovina)'; a pilgrim path running north-south past the chapel "
            "labelled 'IL SENTIERO DEL PELLEGRINO'; a row of tall thin Italian "
            "cypress trees along the western edge labelled 'I CIPRESSI'; a "
            "central stand of small holm oak trees labelled 'IL LECCETO'; a row "
            "of umbrella pines on the eastern boundary labelled 'I PINI'; a tiny "
            "circular Roman cistern labelled 'LA CISTERNA (asciutta)'; and a "
            "small memorial bench labelled 'LA PIETRA BELLINI'. Warm "
            "sienna-red and dusty green watercolor washes over the wooded "
            "area, with pale tan for the open clearings." + MAP_STYLE
        ),
    },
    # ---- KRASNODAR ----------------------------------------------------------
    {
        "filename": "map-krasnodar.png",
        "size": "1536x1024",
        "prompt": (
            "An illustrated estate map of a Russian woodland titled 'СТО-АКРОВЫЙ "
            "ЛЕС' in large hand-lettered Cyrillic serif at the top, subtitled "
            "below in smaller hand-lettered Latin script 'Krasnodar Krai · "
            "обследован осенью MMXXIV'. The wood is on a mountain slope; brown "
            "ink contour lines indicate the rising elevation from south (lower) "
            "to north (higher). Features shown and labelled by hand: an avenue "
            "of Caucasian beech trees on the lower slope labelled 'БУКОВАЯ "
            "АЛЛЕЯ' (beech avenue), a crest of tall silver fir trees (pointed "
            "conifer shapes) along the upper slope labelled 'ПИХТОВЫЙ ГРЕБЕНЬ' "
            "(fir crest), a small stream winding from the upper crest down to "
            "the eastern boundary labelled 'МЕДВЕЖИЙ РУЧЕЙ' (bear stream), a "
            "tiny wooden bridge crossing the stream labelled 'МОСТ' (bridge), a "
            "tiny wardens' lodge near the eastern boundary labelled 'ДОМ "
            "ЛЕСНИКА' (warden's lodge), and a small upright memorial stone on "
            "the east edge marked '1944'. Cool slate-blue and silver-green "
            "watercolor washes for the conifer-heavy slope; pale sage for the "
            "beech avenue." + MAP_STYLE
        ),
    },
]


def all_images():
    return IMAGES + MAPS


def generate(force: bool = False) -> None:
    client = OpenAI()  # reads OPENAI_API_KEY from env
    images = all_images()
    total = len(images)
    skipped = 0
    failed = []

    for i, img in enumerate(images, 1):
        out = OUT_DIR / img["filename"]
        # Also treat a converted .jpg version as "exists" so reruns are cheap
        jpg = out.with_suffix(".jpg")
        if (out.exists() or jpg.exists()) and not force:
            print(f"[{i:>2}/{total}] skip  {img['filename']} (exists)", flush=True)
            skipped += 1
            continue

        print(f"[{i:>2}/{total}] gen   {img['filename']} ({img['size']})...", flush=True)
        t0 = time.time()
        try:
            result = client.images.generate(
                model="gpt-image-2",
                prompt=img["prompt"],
                size=img["size"],
                quality="medium",
                n=1,
            )
            b64 = result.data[0].b64_json
            out.write_bytes(base64.b64decode(b64))
            dt = time.time() - t0
            kb = out.stat().st_size // 1024
            print(f"           saved → {out.relative_to(OUT_DIR.parent.parent)} ({kb} KB, {dt:.1f}s)", flush=True)
        except Exception as e:
            print(f"           FAILED: {e}", flush=True)
            failed.append(img["filename"])

    print()
    print(f"Done. {total - skipped - len(failed)} generated, {skipped} skipped, {len(failed)} failed.")
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="regenerate even if file exists")
    args = p.parse_args()
    generate(force=args.force)
