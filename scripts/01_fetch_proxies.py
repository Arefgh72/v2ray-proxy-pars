# --- V2Ray Proxy Parser - Fetch and Extract Configurations ---
from curl_cffi.requests import get
import base64
import os
from pathlib import Path

# Get the repo root directory (parent of scripts folder)
REPO_ROOT = Path(__file__).parent.parent
SUBSCRIPTIONS_FILE_PATH = REPO_ROOT / 'config' / 'subscriptions.txt'
RAW_PROXIES_OUTPUT_PATH = REPO_ROOT / 'output' / 'raw_proxies.txt'
V2RAY_CONFIG_OUTPUT_PATH = REPO_ROOT / 'output' / 'v2ray_config.txt'

def get_subscription_links():
    """
    Read subscription links from the subscriptions.txt file.
    Ignores comments (lines starting with #) and empty lines.
    """
    try:
        with open(SUBSCRIPTIONS_FILE_PATH, 'r') as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"✓ Found {len(links)} subscription links in '{SUBSCRIPTIONS_FILE_PATH}'.")
        return links
    except FileNotFoundError:
        print(f"✗ Error: {SUBSCRIPTIONS_FILE_PATH} not found.")
        print(f"   Current path: {os.getcwd()}")
        print(f"   Looking for: {SUBSCRIPTIONS_FILE_PATH}")
        return []
    except Exception as e:
        print(f"✗ Error reading subscription file: {str(e)}")
        return []

def fetch_and_decode_link(link: str) -> list[str]:
    """
    Fetch proxy configuration from a subscription link.
    Supports Base64 encoded and plain text formats.
    Returns a list of valid proxy URLs.
    """
    clean_link = link.split('#')[0].strip()
    try:
        print(f"  → Fetching: {clean_link[:70]}...")
        
        # Fetch with Chrome browser impersonation
        response = get(clean_link, timeout=30, impersonate="chrome110")
        response.raise_for_status()
        
        content = response.text
        proxies = []

        try:
            # Try to decode as Base64
            decoded_content = base64.b64decode(content).decode('utf-8')
            proxies = decoded_content.splitlines()
            print(f"    ✓ Decoded as Base64")
        except Exception:
            # If Base64 decoding fails, treat as plain text
            proxies = content.splitlines()
            print(f"    ✓ Processed as Plain Text")

        # Filter only valid proxy protocols
        VALID_PROTOCOLS = ('vmess://', 'vless://', 'trojan://', 'ss://', 'hy://', 'hysteria://', 'hy2://')
        valid_proxies = [p.strip() for p in proxies if p.strip().startswith(VALID_PROTOCOLS)]
        print(f"    ✓ Found {len(valid_proxies)} valid proxies")
        return valid_proxies

    except Exception as e:
        print(f"    ✗ Failed to fetch from {clean_link[:50]}... Error: {str(e)}")
        return []

def main():
    """
    Main execution flow:
    1. Read subscription links from config/subscriptions.txt
    2. Fetch and decode proxies from each link
    3. Save raw proxies to output/raw_proxies.txt
    4. Extract and save V2Ray configurations to output/v2ray_config.txt
    """
    print("\n" + "="*60)
    print("V2Ray Proxy Parser - Fetching Configurations")
    print("="*60)
    print(f"Repository Root: {REPO_ROOT}")
    
    os.makedirs(REPO_ROOT / 'output', exist_ok=True)
    
    # Step 1: Get subscription links
    subscription_links = get_subscription_links()
    if not subscription_links:
        print("✗ No subscription links found. Exiting.")
        return

    # Step 2: Fetch all proxies
    print("\n[*] Fetching proxies from subscription links...")
    all_proxies = []
    for link in subscription_links:
        all_proxies.extend(fetch_and_decode_link(link))

    # Step 3: Remove duplicates
    unique_proxies = list(dict.fromkeys(all_proxies))
    print(f"\n✓ Total unique proxies fetched: {len(unique_proxies)}")

    # Step 4: Save raw proxies and V2Ray config
    if unique_proxies:
        # Save raw proxies
        with open(RAW_PROXIES_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_proxies))
        print(f"✓ Saved {len(unique_proxies)} proxies to '{RAW_PROXIES_OUTPUT_PATH}'")

        # Save V2Ray configurations (same as raw proxies in this case)
        with open(V2RAY_CONFIG_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_proxies))
        print(f"✓ Saved V2Ray configuration to '{V2RAY_CONFIG_OUTPUT_PATH}'")
    else:
        print("✗ No proxies were fetched.")

    print("\n" + "="*60)
    print("Done!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
