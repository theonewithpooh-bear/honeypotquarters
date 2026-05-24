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


def generate(force: bool = False) -> None:
    client = OpenAI()  # reads OPENAI_API_KEY from env
    total = len(IMAGES)
    skipped = 0
    failed = []

    for i, img in enumerate(IMAGES, 1):
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
