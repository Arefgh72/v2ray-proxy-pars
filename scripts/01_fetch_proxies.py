# --- Main Feature: Using curl_cffi with Browser Impersonation ---
from curl_cffi.requests import get
import base64
import os
from .utils import log_error

SUBSCRIPTIONS_FILE_PATH = 'config/subscriptions.txt'
RAW_PROXIES_OUTPUT_PATH = 'output/raw_proxies.txt'
V2RAY_CONFIG_OUTPUT_PATH = 'output/v2ray_config.txt'

def get_subscription_links():
    """
    Read subscription links from the subscriptions.txt file.
    Ignores comments (lines starting with #) and empty lines.
    """
    try:
        with open(SUBSCRIPTIONS_FILE_PATH, 'r') as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"Found {len(links)} subscription links in '{SUBSCRIPTIONS_FILE_PATH}'.")
        return links
    except Exception as e:
        log_error("Fetch Proxies", "Error reading subscription file.", str(e))
        return []

def fetch_and_decode_link(link: str) -> list[str]:
    """
    Fetch proxy configuration from a subscription link.
    Supports Base64 encoded and plain text formats.
    Returns a list of valid proxy URLs (vmess, vless, trojan, ss, hy, hysteria, hy2).
    """
    clean_link = link.split('#')[0].strip()
    try:
        print(f"Fetching: {clean_link[:80]}...")
        # --- Main Feature: Using impersonate to mimic Chrome browser ---
        response = get(clean_link, timeout=30, impersonate="chrome110")
        response.raise_for_status()
        
        content = response.text
        proxies = []

        try:
            # Try to decode as Base64
            decoded_content = base64.b64decode(content).decode('utf-8')
            proxies = decoded_content.splitlines()
            print(f"  -> Decoded as Base64.")
        except Exception:
            # If Base64 decoding fails, treat as plain text
            proxies = content.splitlines()
            print(f"  -> Processed as Plain Text.")

        # Filter only valid proxy protocols
        VALID_PROTOCOLS = ('vmess://', 'vless://', 'trojan://', 'ss://', 'hy://', 'hysteria://', 'hy2://')
        valid_proxies = [p.strip() for p in proxies if p.strip().startswith(VALID_PROTOCOLS)]
        print(f"  -> Found {len(valid_proxies)} valid proxies.")
        return valid_proxies

    except Exception as e:
        log_error("Fetch Proxies (Network)", f"Failed to fetch from link: {clean_link}", str(e))
        return []

def extract_v2ray_configs(proxies: list[str]) -> str:
    """
    Extract and format V2Ray configurations from proxy URLs.
    Returns formatted configuration string for v2ray_config.txt
    """
    v2ray_configs = []
    
    for proxy in proxies:
        if proxy.startswith(('vmess://', 'vless://', 'trojan://', 'ss://', 'hy://', 'hysteria://', 'hy2://')):
            v2ray_configs.append(proxy)
    
    return '\n'.join(v2ray_configs)

def main():
    """
    Main execution flow:
    1. Read subscription links from config/subscriptions.txt
    2. Fetch and decode proxies from each link
    3. Save raw proxies to output/raw_proxies.txt
    4. Extract and save V2Ray configurations to output/v2ray_config.txt
    """
    print("--- Running 01_fetch_proxies.py (with Browser Impersonation) ---")
    os.makedirs('output', exist_ok=True)
    
    # Step 1: Get subscription links
    subscription_links = get_subscription_links()
    if not subscription_links:
        print("No subscription links found.")
        return

    # Step 2: Fetch all proxies
    print("\n--- Fetching proxies from subscription links ---")
    all_proxies = []
    for link in subscription_links:
        all_proxies.extend(fetch_and_decode_link(link))

    # Step 3: Remove duplicates
    unique_proxies = list(dict.fromkeys(all_proxies))
    print(f"\nTotal unique proxies fetched: {len(unique_proxies)}")

    # Step 4: Save raw proxies
    if unique_proxies:
        with open(RAW_PROXIES_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_proxies))
        print(f"Successfully saved {len(unique_proxies)} proxies to '{RAW_PROXIES_OUTPUT_PATH}'.")

        # Step 5: Extract and save V2Ray configurations
        print("\n--- Extracting V2Ray configurations ---")
        v2ray_config_content = extract_v2ray_configs(unique_proxies)
        with open(V2RAY_CONFIG_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(v2ray_config_content)
        print(f"Successfully saved V2Ray configuration to '{V2RAY_CONFIG_OUTPUT_PATH}'.")
    else:
        print("No proxies were fetched.")

    print("--- Finished 01_fetch_proxies.py ---")

if __name__ == "__main__":
    main()
