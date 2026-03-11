#!/usr/bin/env python3
"""
Nano Banana B-Roll Video Generator (Google Gemini Veo API)
==========================================================
Sends prompts to Google's Veo 3.1 via the Gemini API, polls for
completion, and downloads generated video clips for CapCut/Descript editing.

Zero external dependencies — Python stdlib only.

Usage:
    python3 scripts/generate-broll.py                        # All clips
    python3 scripts/generate-broll.py --version 90s          # Just 90s
    python3 scripts/generate-broll.py --version 90s --clip 1 # Single clip
    python3 scripts/generate-broll.py --dry-run              # Preview only
"""

import argparse
import json
import os
import signal
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROMPTS_FILE = SCRIPT_DIR / "broll-prompts.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "broll-output"

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
VEO_MODEL = "veo-3.1-generate-preview"
DEFAULT_DURATION = 8       # Veo supports 4, 6, or 8 seconds
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "720p"  # 720p, 1080p, or 4k
DEFAULT_POLL_INTERVAL = 10  # seconds (Google recommends 10s)
DEFAULT_MAX_RETRIES = 3
POLL_TIMEOUT = 600  # 10 minutes

# ---------------------------------------------------------------------------
# .env loader (no dependencies)
# ---------------------------------------------------------------------------

def load_dotenv(path: Path) -> None:
    """Load .env file into os.environ. Skips comments and blank lines."""
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


# ---------------------------------------------------------------------------
# API Client — Google Gemini Veo
# ---------------------------------------------------------------------------

class VeoClient:
    """Minimal HTTP client for Google Gemini Veo video generation API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, method: str, url: str, body: dict = None) -> dict:
        """Make an API request. Returns parsed JSON."""
        # Append API key as query parameter
        separator = "&" if "?" in url else "?"
        full_url = f"{url}{separator}key={self.api_key}"

        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(full_url, data=data, method=method)
        req.add_header("Content-Type", "application/json")

        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())

    def generate(self, prompt: str, duration: int = 8,
                 resolution: str = "720p",
                 aspect_ratio: str = "16:9") -> dict:
        """Submit a video generation request. Returns operation info."""
        url = f"{API_BASE}/models/{VEO_MODEL}:predictLongRunning"
        return self._request("POST", url, {
            "instances": [{
                "prompt": prompt,
            }],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "resolution": resolution,
                "durationSeconds": duration,
            }
        })

    def poll_status(self, operation_name: str) -> dict:
        """Check the status of a generation operation."""
        url = f"{API_BASE}/{operation_name}"
        return self._request("GET", url)

    def wait_for_completion(self, operation_name: str, poll_interval: int = 10,
                            timeout: int = 600) -> dict:
        """Poll until operation completes or times out."""
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                return {"done": False, "error": f"Timed out after {timeout}s",
                        "name": operation_name}

            status = self.poll_status(operation_name)

            if status.get("done"):
                return status

            if "error" in status:
                return status

            remaining = timeout - elapsed
            wait = min(poll_interval, remaining)
            print(f"    Generating... polling in {int(wait)}s "
                  f"(elapsed: {int(elapsed)}s)")
            time.sleep(wait)

    def download(self, url: str, dest: Path) -> None:
        """Download a video file from URL to local path."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Google video URIs need the API key
        separator = "&" if "?" in url else "?"
        full_url = f"{url}{separator}key={self.api_key}"
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req) as resp:
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def load_manifest(output_dir: Path) -> dict:
    """Load existing manifest or return empty structure."""
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {"generated": [], "failed": [], "skipped": [],
            "last_run": None, "total_clips": 0}


def save_manifest(output_dir: Path, manifest: dict) -> None:
    """Write manifest to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def build_filename(version: str, scene: int, slug: str) -> str:
    """Build output filename like 90s-scene-01-the-problem.mp4"""
    return f"{version}-scene-{scene:02d}-{slug}.mp4"


def get_clips(prompts: dict, version: str = None, clip: int = None) -> list:
    """Filter clips by version and/or clip number. Returns list of
    (version_key, clip_data) tuples."""
    results = []
    for ver_key, ver_data in prompts["versions"].items():
        if version and ver_key != version:
            continue
        for c in ver_data["clips"]:
            if clip is not None and c["scene"] != clip:
                continue
            results.append((ver_key, c))
    return results


def run_generation(clips: list, client: VeoClient, output_dir: Path,
                   duration: int, resolution: str, aspect_ratio: str,
                   force: bool, poll_interval: int, max_retries: int,
                   dry_run: bool) -> dict:
    """Process all clips. Returns manifest data."""
    manifest = load_manifest(output_dir)
    total = len(clips)

    # Track already-generated filenames for skip logic
    existing_files = {e["filename"] for e in manifest.get("generated", [])}

    for i, (ver_key, clip_data) in enumerate(clips, 1):
        filename = build_filename(ver_key, clip_data["scene"], clip_data["slug"])
        dest = output_dir / ver_key / filename

        print(f"\n[{i}/{total}] {filename}")
        print(f"  Title:  {clip_data['title']}")
        print(f"  Prompt: {clip_data['prompt'][:80]}...")

        if dry_run:
            print(f"  Output: {dest}")
            print("  [DRY RUN — skipped]")
            continue

        # Skip existing unless --force
        if dest.exists() and not force:
            print(f"  File exists — skipping (use --force to regenerate)")
            if filename not in existing_files:
                manifest["skipped"].append({
                    "filename": filename,
                    "reason": "already_exists",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            continue

        # Submit generation request with retries
        operation_name = None
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  Submitting to Veo API (attempt {attempt}/{max_retries})...")
                result = client.generate(
                    clip_data["prompt"], duration, resolution, aspect_ratio)
                operation_name = result.get("name")
                if operation_name:
                    print(f"  Operation: {operation_name}")
                    break
                else:
                    print(f"  Unexpected response: {json.dumps(result)[:200]}")
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode()
                except Exception:
                    pass
                if e.code in (401, 403):
                    print(f"  ERROR: Auth failed ({e.code}). Check your API key.")
                    if body:
                        print(f"  Detail: {body[:200]}")
                    save_manifest(output_dir, manifest)
                    sys.exit(1)
                if e.code == 429:
                    retry_after = int(e.headers.get("Retry-After", 30))
                    print(f"  Rate limited ({e.code}) — waiting {retry_after}s...")
                    if body:
                        print(f"  Detail: {body[:300]}")
                    time.sleep(retry_after)
                    continue
                if e.code >= 500 and attempt < max_retries:
                    wait = 2 ** attempt
                    print(f"  Server error ({e.code}) — retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                print(f"  HTTP Error {e.code}: {e.reason}")
                if body:
                    print(f"  Detail: {body[:300]}")
                break
            except Exception as e:
                print(f"  Error: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break

        if not operation_name:
            print("  FAILED — could not submit job")
            manifest["failed"].append({
                "filename": filename,
                "error": "submit_failed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # Poll for completion
        print("  Waiting for video generation...")
        status = client.wait_for_completion(
            operation_name, poll_interval, POLL_TIMEOUT)

        if not status.get("done"):
            error = status.get("error", "unknown")
            print(f"  FAILED — {error}")
            manifest["failed"].append({
                "filename": filename,
                "operation": operation_name,
                "error": str(error),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # Extract video URI from response
        # Response shape: { done: true, response: { generateVideoResponse:
        #   { generatedSamples: [{ video: { uri: "..." } }] } } }
        try:
            samples = (status.get("response", {})
                       .get("generateVideoResponse", {})
                       .get("generatedSamples", []))
            video_uri = samples[0]["video"]["uri"] if samples else None
        except (KeyError, IndexError):
            video_uri = None

        if not video_uri:
            print("  FAILED — no video URI in response")
            manifest["failed"].append({
                "filename": filename,
                "operation": operation_name,
                "error": "no_video_uri",
                "response": str(status)[:500],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            continue

        # Download the video
        print(f"  Downloading → {dest}")
        try:
            client.download(video_uri, dest)
            size_mb = dest.stat().st_size / (1024 * 1024)
            print(f"  Done ({size_mb:.1f} MB)")
            manifest["generated"].append({
                "filename": filename,
                "operation": operation_name,
                "version": ver_key,
                "scene": clip_data["scene"],
                "slug": clip_data["slug"],
                "path": str(dest),
                "size_bytes": dest.stat().st_size,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            print(f"  Download failed: {e}")
            manifest["failed"].append({
                "filename": filename,
                "operation": operation_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    manifest["total_clips"] = total
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate B-roll video clips via Google Gemini Veo API")
    p.add_argument("--version", choices=["90s", "60s", "30s"],
                   help="Generate only this version")
    p.add_argument("--clip", type=int,
                   help="Generate only this scene number")
    p.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                   choices=[4, 6, 8],
                   help=f"Clip duration in seconds (default: {DEFAULT_DURATION})")
    p.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                   choices=["720p", "1080p", "4k"],
                   help=f"Video resolution (default: {DEFAULT_RESOLUTION})")
    p.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                   choices=["16:9", "9:16"],
                   help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO})")
    p.add_argument("--dry-run", action="store_true",
                   help="Preview prompts and filenames without calling API")
    p.add_argument("--force", action="store_true",
                   help="Regenerate even if file already exists")
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT,
                   help=f"Output directory (default: {DEFAULT_OUTPUT})")
    p.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                   help=f"Seconds between status polls (default: {DEFAULT_POLL_INTERVAL})")
    p.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                   help=f"Max retries on failure (default: {DEFAULT_MAX_RETRIES})")
    return p.parse_args()


def main():
    args = parse_args()

    # Load prompts
    if not PROMPTS_FILE.exists():
        print(f"ERROR: Prompts file not found: {PROMPTS_FILE}")
        sys.exit(1)
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)

    # Filter clips
    clips = get_clips(prompts, args.version, args.clip)
    if not clips:
        print("No clips match the given filters.")
        sys.exit(1)

    print(f"Nano Banana B-Roll Generator (Veo {VEO_MODEL})")
    print(f"{'=' * 50}")
    print(f"Clips to process: {len(clips)}")
    print(f"Duration: {args.duration}s  |  Resolution: {args.resolution}  |  "
          f"Aspect: {args.aspect_ratio}")
    print(f"Output: {args.output_dir}")
    if args.dry_run:
        print("[DRY RUN MODE — no API calls]")

    # Load API key (skip in dry-run)
    client = None
    if not args.dry_run:
        load_dotenv(PROJECT_ROOT / ".env")
        api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
        if not api_key or api_key == "your-api-key-here":
            print("\nERROR: API key not set.")
            print("Steps:")
            print("  1. Get a Gemini API key from https://aistudio.google.com/apikey")
            print("  2. Add it to .env:  NANO_BANANA_API_KEY=AIzaSy...")
            print("  Or set the environment variable directly.")
            sys.exit(1)
        client = VeoClient(api_key)

    # Handle Ctrl+C gracefully
    manifest = {"generated": [], "failed": [], "skipped": [],
                "last_run": None, "total_clips": 0}

    def handle_interrupt(sig, frame):
        print("\n\nInterrupted — saving manifest with results so far...")
        save_manifest(args.output_dir, manifest)
        print(f"Manifest saved to {args.output_dir / 'manifest.json'}")
        sys.exit(130)

    signal.signal(signal.SIGINT, handle_interrupt)

    # Run
    manifest = run_generation(
        clips, client, args.output_dir,
        args.duration, args.resolution, args.aspect_ratio,
        args.force, args.poll_interval, args.max_retries, args.dry_run)

    # Save manifest (skip in dry-run)
    if not args.dry_run:
        save_manifest(args.output_dir, manifest)
        print(f"\nManifest saved to {args.output_dir / 'manifest.json'}")

    # Summary
    gen = len(manifest.get("generated", []))
    fail = len(manifest.get("failed", []))
    skip = len(manifest.get("skipped", []))
    print(f"\nSummary: {gen} generated, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    main()
