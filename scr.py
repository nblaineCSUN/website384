# save as audit_and_fix_images.py
import os, sys, imghdr, pathlib
from PIL import Image

IMG_DIR = os.path.join("static", "images", "countries")
MIN_BYTES = 1024  # anything smaller is suspicious

def is_html(path):
    try:
        with open(path, "rb") as f:
            head = f.read(2048).lstrip()
        return head.startswith(b"<!DOCTYPE html") or head.startswith(b"<html")
    except:
        return False

def convert_to_jpg(src_path):
    dst_path = os.path.splitext(src_path)[0] + ".jpg"
    try:
        with Image.open(src_path) as im:
            im = im.convert("RGB")
            im.save(dst_path, "JPEG", quality=90, optimize=True)
        if dst_path != src_path:
            os.remove(src_path)
        return dst_path, None
    except Exception as e:
        return None, str(e)

def main():
    if not os.path.isdir(IMG_DIR):
        print(f"Directory not found: {IMG_DIR}")
        sys.exit(1)

    ok, repaired, bad = [], [], []
    for name in sorted(os.listdir(IMG_DIR)):
        p = os.path.join(IMG_DIR, name)
        if not os.path.isfile(p): 
            continue

        size = os.path.getsize(p)
        ext  = os.path.splitext(name)[1].lower()

        if size < MIN_BYTES or is_html(p):
            bad.append((p, "html_or_too_small"))
            continue

        kind = imghdr.what(p)  # 'jpeg','png','gif','tiff','webp', or None
        if kind in ("jpeg", "png", "webp", "tiff", "gif", "bmp"):
            # Convert non-jpeg to jpg for consistency
            if kind != "jpeg" or ext not in (".jpg", ".jpeg"):
                newp, err = convert_to_jpg(p)
                if newp:
                    repaired.append((p, f"{kind}->jpg"))
                else:
                    bad.append((p, f"convert_error:{err}"))
            else:
                ok.append(p)
        else:
            # Might be svg or corrupt
            with open(p, "rb") as f:
                head = f.read(64)
            if b"<svg" in head.lower():
                bad.append((p, "svg_needs_rasterizing"))
            else:
                bad.append((p, f"unknown_format:{kind}"))

    print("\n=== OK images ===")
    for p in ok: print(p)
    print("\n=== Repaired (now .jpg) ===")
    for p, why in repaired: print(why, " -> ", p)
    print("\n=== Problem files (action needed) ===")
    for p, why in bad: print(why, " -> ", p)

if __name__ == "__main__":
    main()
