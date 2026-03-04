# tools/download_tiffs.py
import argparse
import time
from pathlib import Path
import httpx
from pystac_client import Client

STAC_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-c1-l2a"
MAX_RETRIES = 3
RETRY_DELAY = 2


def download_with_retries(href: str, filename: Path) -> bool:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with httpx.stream("GET", href, timeout=60, follow_redirects=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            return True
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            if attempt == MAX_RETRIES:
                print(f"  Failed after {MAX_RETRIES} attempts: {e}")
                return False
            wait = RETRY_DELAY * (2 ** (attempt - 1))
            print(f"  Attempt {attempt} failed ({e}), retrying in {wait}s...")
            time.sleep(wait)
    return False


def download_tiffs(
    bbox: list[float],           # [west, south, east, north]
    start_date: str,             # "2024-01-01"
    end_date: str,               # "2024-12-31"
    output_dir: Path,
    max_items: int = 10,
    max_cloud_cover: int = 20,
    image_key: str = "visual",
):
    output_dir.mkdir(parents=True, exist_ok=True)
    client = Client.open(STAC_URL)

    search = client.search(
        collections=[COLLECTION],
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        max_items=max_items,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        sortby="+properties.eo:cloud_cover",
    )

    items = list(search.items())
    print(f"Found {len(items)} items")

    succeeded, failed = 0, 0
    for item in items:
        href = item.assets[image_key].href
        filename = output_dir / f"{item.id}.tiff"
        print(f"Downloading {item.id}...")
        if download_with_retries(href, filename):
            print(f"  Saved to {filename}")
            succeeded += 1
        else:
            failed += 1

    print(f"\nDone: {succeeded} succeeded, {failed} failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"), required=True)
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--output", type=Path, default=Path("downloads"))
    parser.add_argument("--max-items", type=int, default=10)
    parser.add_argument("--max-cloud-cover", type=int, default=20)
    args = parser.parse_args()

    download_tiffs(
        bbox=args.bbox,
        start_date=args.start,
        end_date=args.end,
        output_dir=args.output,
        max_items=args.max_items,
        max_cloud_cover=args.max_cloud_cover,
    )