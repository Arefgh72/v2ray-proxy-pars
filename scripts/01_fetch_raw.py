#!/usr/bin/env python3
# Simple fetcher: download raw content from subscription links and save as-is.
from curl_cffi.requests import get
from pathlib import Path
import os
import tempfile

REPO_ROOT = Path(__file__).parent.parent
SUBSCRIPTIONS_FILE_PATH = REPO_ROOT / 'config' / 'subscriptions.txt'
RAW_PROXIES_OUTPUT_PATH = REPO_ROOT / 'output' / 'raw_proxies.txt'

def get_subscription_links():
    try:
        with open(SUBSCRIPTIONS_FILE_PATH, 'r', encoding='utf-8') as f:
            links = []
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                links.append(line)
        print(f"✓ Found {len(links)} subscription links in '{SUBSCRIPTIONS_FILE_PATH}'.")
        return links
    except FileNotFoundError:
        print(f"✗ Error: {SUBSCRIPTIONS_FILE_PATH} not found.")
        return []
    except Exception as e:
        print(f"✗ Error reading subscription file: {e}")
        return []

def fetch_raw_content(url: str) -> str:
    clean = url.split('#', 1)[0].strip()
    try:
        print(f"  → Fetching: {clean[:80]}...")
        resp = get(clean, timeout=30, impersonate="chrome110")
        resp.raise_for_status()
        # Return raw text exactly as received (no decoding, no filtering)
        return resp.text
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return ""

def atomic_write(path: Path, text: str, encoding='utf-8'):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + '.', text=True)
    try:
        with os.fdopen(fd, 'w', encoding=encoding) as fh:
            fh.write(text)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        raise

def main():
    print("\n" + "="*40)
    print("Raw Subscription Fetcher - Save content as-is")
    print("="*40 + "\n")

    links = get_subscription_links()
    if not links:
        print("✗ No links to fetch. Exiting.")
        return

    pieces = []
    for i, link in enumerate(links, start=1):
        content = fetch_raw_content(link)
        if content:
            # Append raw content exactly; add a single newline between sources to separate
            pieces.append(content)
        else:
            print(f"    ⚠ Skipped link #{i} (no content).")

    combined = "\n".join(pieces)
    if not combined:
        print("✗ No content fetched from any subscription.")
        return

    try:
        atomic_write(RAW_PROXIES_OUTPUT_PATH, combined)
        print(f"✓ Saved raw content to '{RAW_PROXIES_OUTPUT_PATH}' ({len(pieces)} sources).")
    except Exception as e:
        print(f"✗ Failed to write output file: {e}")

if __name__ == '__main__':
    main()
