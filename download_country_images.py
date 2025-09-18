#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download FRUIT images (not flags) for each row in fruit_facts, save to static/images/spacefruit,
and update fruit_facts.fruit_image with the saved path.

- Pulls fruit names from SQLite (joins countries for nice filenames)
- Targets fruit-specific Wikipedia pages (uses overrides for ambiguous names, e.g. "Date (fruit)")
- Validates Content-Type to avoid saving HTML by mistake
- Converts PNG/WEBP/GIF/TIFF to JPG (via Pillow) for consistency
- Optionally rasterizes SVG if cairosvg is installed
- Writes a CSV manifest of statuses

Run:
  pip install requests pillow
  # optional for SVG pages:
  pip install cairosvg
  python download_fruit_images_and_update_db.py
"""

import os
import re
import csv
import time
import sqlite3
import pathlib
import unicodedata
from io import BytesIO
from typing import Optional, Dict, List, Tuple

import requests
from PIL import Image

# ---------- Paths ----------
# Matches your Flask app’s default DB location: db/fruit.db next to the script/app
# (same as your Flask code’s construction).
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "fruit.db")
OUTPUT_DIR = os.path.join("static", "images", "spacefruit")
MANIFEST_CSV = os.path.join(OUTPUT_DIR, "_fruit_download_manifest.csv")

# ---------- HTTP ----------
HEADERS = {
    "User-Agent": "FruitStandFruitImageFetcher/1.0 (contact: youremail@example.com)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}
TIMEOUT = 60
PAUSE_BETWEEN = 0.5  # politeness

# Try optional SVG rasterizer
try:
    import cairosvg  # type: ignore
    HAS_CAIROSVG = True
except Exception:
    HAS_CAIROSVG = False

# ---------- Fruit title overrides (avoid flags, disambiguate) ----------
FRUIT_TITLE_OVERRIDES: Dict[str, List[str]] = {
    # Ambiguous or better-specific targets first:
    "Date": ["Date (fruit)", "Date palm"],
    "Plantain": ["Cooking banana", "Plantain (banana)"],
    "Finger Lime": ["Finger lime", "Citrus australasica"],
    "Açaí": ["Açaí palm", "Euterpe oleracea", "Açaí"],
    "Acai": ["Açaí palm", "Euterpe oleracea", "Açaí"],  # fallback without diacritic
    "Cocoa Pod": ["Theobroma cacao", "Cocoa bean", "Cacao"],
    "Orange": ["Orange (fruit)", "Sweet orange", "Citrus × sinensis"],
    "Fig": ["Common fig", "Ficus carica"],
    # Straightforward fruit pages (still listed for consistency):
    "Pomegranate": ["Pomegranate"],
    "Olive": ["Olive"],
    "Apple": ["Apple"],
    "Banana": ["Banana"],
    "Mango": ["Mango"],
    "Papaya": ["Papaya"],
    "Guava": ["Guava"],
    "Pineapple": ["Pineapple"],
    "Jackfruit": ["Jackfruit"],
    "Breadfruit": ["Breadfruit"],
    "Cherry": ["Cherry"],
    "Strawberry": ["Strawberry"],
    "Blueberry": ["Blueberry"],
    "Durian": ["Durian"],
    "Coconut": ["Coconut"],
    "Lychee": ["Lychee"],
    "Plum": ["Plum"],
    "Melon": ["Melon"],
}

# ---------- Utilities ----------
def ensure_dir(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def ascii_slug(s: str) -> str:
    # Strip diacritics, keep a-z0-9- only
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s

def db_query_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    with con:
        cur = con.execute(query, params)
        rows = cur.fetchall()
    con.close()
    return rows

def db_execute(query: str, params: tuple = ()) -> None:
    con = sqlite3.connect(DB_PATH)
    with con:
        con.execute(query, params)
    con.close()

# ---------- Wikipedia helpers ----------
def pick_ext_from_content_type(ct: Optional[str]) -> Optional[str]:
    if not ct:
        return None
    ct = ct.lower().split(";")[0].strip()
    return {
        "image/jpeg": ".jpg",
        "image/jpg":  ".jpg",
        "image/png":  ".png",
        "image/webp": ".webp",
        "image/gif":  ".gif",
        "image/bmp":  ".bmp",
        "image/tiff": ".tif",
        "image/svg+xml": ".svg",
    }.get(ct)

def wikipedia_image_url(title: str) -> Optional[str]:
    """
    Use pageimages: try original; fallback to a large thumbnail.
    """
    base = "https://en.wikipedia.org/w/api.php"

    # Try original image
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "titles": title,
        "piprop": "original",
        "origin": "*",
    }
    r = requests.get(base, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        if "original" in page and "source" in page["original"]:
            return page["original"]["source"]

    # Fallback big thumbnail
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "titles": title,
        "pithumbsize": "2000",
        "origin": "*",
    }
    r = requests.get(base, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        thumb = page.get("thumbnail")
        if thumb and "source" in thumb:
            return thumb["source"]

    return None

def svg_bytes_to_jpg(svg_bytes: bytes, dest_without_ext: str, width: int = 2000) -> str:
    if not HAS_CAIROSVG:
        raise RuntimeError("cairosvg not installed")
    png_bytes = cairosvg.svg2png(bytestring=svg_bytes, output_width=width)
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    out = dest_without_ext + ".jpg"
    img.save(out, "JPEG", quality=90, optimize=True)
    return out

def save_image_from_url(url: str, dest_without_ext: str) -> Tuple[Optional[str], str]:
    """
    Download URL → file. Converts raster formats to JPG using Pillow.
    Returns (saved_path, status_or_content_type). On failure: (None, reason).
    """
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        return None, f"http_error:{type(e).__name__}"

    ct = (r.headers.get("Content-Type") or "").lower()
    if "text/html" in ct:
        return None, "got_html_not_image"

    buf = BytesIO()
    for chunk in r.iter_content(8192):
        if chunk:
            buf.write(chunk)
    b = buf.getvalue()
    if len(b) < 1024:
        return None, "too_small"

    ext = pick_ext_from_content_type(ct) or os.path.splitext(url.split("?")[0])[1].lower()
    if not ext or len(ext) > 5:
        ext = ".jpg"

    if ext == ".svg":
        if not HAS_CAIROSVG:
            return None, "svg_requires_cairosvg"
        try:
            saved = svg_bytes_to_jpg(b, dest_without_ext, width=2000)
            return saved, ct
        except Exception as e:
            return None, f"svg_rasterize_error:{type(e).__name__}"

    # Convert raster to JPG for consistency
    try:
        img = Image.open(BytesIO(b)).convert("RGB")
        out = dest_without_ext + ".jpg"
        img.save(out, "JPEG", quality=90, optimize=True)
        return out, ct
    except Exception as e:
        # As a last resort, save raw bytes with their ext
        out = dest_without_ext + ext
        with open(out, "wb") as f:
            f.write(b)
        return out, f"saved_raw_due_to:{type(e).__name__}"

# ---------- Main ----------
def main() -> None:
    ensure_dir(OUTPUT_DIR)

    # Fetch fruit list (join for country slug/name so filenames are unique & readable)
    rows = db_query_all("""
        SELECT ff.id AS fact_id,
               c.id  AS country_id,
               c.slug AS country_slug,
               c.name AS country_name,
               ff.fruit AS fruit
        FROM fruit_facts ff
        JOIN countries c ON c.id = ff.country_id
        ORDER BY c.name ASC
        LIMIT 50
    """)

    results = []
    for row in rows:
        fact_id = row["fact_id"]
        country_slug = row["country_slug"]
        country_name = row["country_name"]
        fruit_name = row["fruit"].strip()

        # Build filename like "cote-divoire-cocoa-pod.jpg"
        fname = f"{ascii_slug(country_slug)}-{ascii_slug(fruit_name)}"
        dest_noext = os.path.join(OUTPUT_DIR, fname)

        # Decide candidate page titles for this fruit
        candidates: List[str] = []
        if fruit_name in FRUIT_TITLE_OVERRIDES:
            candidates.extend(FRUIT_TITLE_OVERRIDES[fruit_name])

        # Sensible defaults if not overridden
        base_variants = [
            f"{fruit_name} (fruit)",
            f"{fruit_name} (plant)",
            fruit_name,
        ]
        for t in base_variants:
            if t not in candidates:
                candidates.append(t)

        image_url = None
        status = "not_found"
        tried = []

        # Try each candidate until one yields an image
        for title in candidates:
            tried.append(title)
            try:
                url = wikipedia_image_url(title)
            except Exception as e:
                url = None
                status = f"wikipedia_api_error:{type(e).__name__}"

            if url:
                saved_path, ctype_or_reason = save_image_from_url(url, dest_noext)
                if saved_path:
                    status = "ok"
                    rel_saved = os.path.relpath(saved_path).replace("\\", "/")
                    # Update DB with the path (relative to /static)
                    # We store "static/images/spacefruit/..." for easy url_for('static', filename=...)
                    rel_for_db = "static/images/spacefruit/" + os.path.basename(rel_saved)
                    try:
                        db_execute(
                            "UPDATE fruit_facts SET fruit_image = ? WHERE id = ?",
                            (rel_for_db, fact_id)
                        )
                    except Exception as e:
                        status = f"db_update_error:{type(e).__name__}"

                    results.append({
                        "country": country_name,
                        "fruit": fruit_name,
                        "saved_as": rel_for_db,
                        "image_url": url,
                        "status": status,
                        "content_type": ctype_or_reason,
                        "tried_titles": " | ".join(tried),
                    })
                    break
                else:
                    status = ctype_or_reason

            time.sleep(0.25)

        if status != "ok":
            results.append({
                "country": country_name,
                "fruit": fruit_name,
                "saved_as": "",
                "image_url": image_url or "",
                "status": status,
                "content_type": "",
                "tried_titles": " | ".join(tried),
            })

        time.sleep(PAUSE_BETWEEN)

    # Write manifest
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["country","fruit","saved_as","image_url","status","content_type","tried_titles"]
        )
        writer.writeheader()
        writer.writerows(results)

    ok = sum(1 for r in results if r["status"] == "ok")
    nf = sum(1 for r in results if r["status"] == "not_found")
    print(f"Done. Saved fruit images in: {OUTPUT_DIR}")
    print(f"Manifest: {MANIFEST_CSV}")
    print(f"Downloaded OK: {ok} | Not found: {nf}")
    leftover = [r for r in results if r["status"] not in ("ok","not_found")]
    if leftover:
        print("Other statuses encountered:")
        for r in leftover:
            print(f" - {r['country']} / {r['fruit']}: {r['status']}")

if __name__ == "__main__":
    main()
