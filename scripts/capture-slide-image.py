#!/usr/bin/env python3
"""
Capture webpage screenshots or download images for slide visuals.

Usage:
  # Screenshot a webpage (Playwright)
  python3 scripts/capture-slide-image.py "https://sam.gov" --lesson 1-3-1 --slide "what is sam.gov?" --name sam-homepage
  python3 scripts/capture-slide-image.py "https://www.dnb.com/duns-number" --lesson 1-1-2 --slide "what is duns?" --name duns-info

  # Download an image directly (no Playwright needed)
  python3 scripts/capture-slide-image.py "https://example.com/image.png" --lesson 1-1-1 --slide "comparison" --download

Saves to assets/images/ and prints the SLIDE_IMAGES entry to add to build-individual-slides.py.

Requires for screenshots: pip install playwright && playwright install chromium
"""

import argparse
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_IMAGES = ROOT / "assets" / "images"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def slugify(s: str) -> str:
    """Create a safe filename from a string."""
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:50].strip("-")


def main():
    parser = argparse.ArgumentParser(description="Capture webpage screenshot for slide visuals")
    parser.add_argument("url", help="URL to capture (e.g. https://sam.gov)")
    parser.add_argument("--lesson", "-l", required=True, help="Lesson ID (e.g. 1-3-1)")
    parser.add_argument("--slide", "-s", required=True, help="Slide title (e.g. 'what is sam.gov?')")
    parser.add_argument("--name", "-n", help="Filename (without extension). Default: slug from slide title")
    parser.add_argument("--selector", help="CSS selector to capture a specific element")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument("--wait", type=int, default=2000, help="Wait ms after load (default: 2000)")
    parser.add_argument("--width", type=int, default=960, help="Viewport width (default: 960)")
    parser.add_argument("--height", type=int, default=540, help="Viewport height (default: 540)")
    parser.add_argument("--download", "-d", action="store_true", help="Download image URL directly (no screenshot)")
    args = parser.parse_args()

    name = args.name or slugify(args.slide)
    ASSETS_IMAGES.mkdir(parents=True, exist_ok=True)

    # Direct image download (no Playwright)
    if args.download or any(args.url.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
        ext = Path(args.url).suffix.split("?")[0] or ".png"
        if ext not in IMAGE_EXTENSIONS:
            ext = ".png"
        filename = f"{name}{ext}"
        out_path = ASSETS_IMAGES / filename
        urllib.request.urlretrieve(args.url, out_path)
        rel_path = f"../../assets/images/{filename}"
        slide_key = args.slide.lower().strip()
        print(f"\nSaved: {out_path}\n")
        print("Add this to SLIDE_IMAGES in scripts/build-individual-slides.py:")
        print(f'    ("{args.lesson}", "{slide_key}"): "{rel_path}",')
        print("\nThen run: python3 scripts/build-individual-slides.py && python3 scripts/build-review-dashboard-28.py")
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed. Run:", file=sys.stderr)
        print("  pip install playwright", file=sys.stderr)
        print("  playwright install chromium", file=sys.stderr)
        sys.exit(1)

    filename = f"{name}.png"
    out_path = ASSETS_IMAGES / filename

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(args.url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(args.wait)

        if args.selector:
            locator = page.locator(args.selector).first
            locator.screenshot(path=str(out_path))
        else:
            page.screenshot(path=str(out_path), full_page=args.full_page)

        browser.close()

    rel_path = f"../../assets/images/{filename}"
    slide_key = args.slide.lower().strip()

    print(f"\nSaved: {out_path}\n")
    print("Add this to SLIDE_IMAGES in scripts/build-individual-slides.py:")
    print(f'    ("{args.lesson}", "{slide_key}"): "{rel_path}",')
    print("\nThen run: python3 scripts/build-individual-slides.py && python3 scripts/build-review-dashboard-28.py")


if __name__ == "__main__":
    main()
