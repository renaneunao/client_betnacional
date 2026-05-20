import json
import os
from urllib.parse import urlparse

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    domains = set()
    for flow in flows:
        url = flow.get("url", "")
        parsed = urlparse(url)
        domains.add(parsed.netloc)

    print("Unique domains in captured flows:")
    for d in sorted(domains):
        print(f" - {d}")

if __name__ == "__main__":
    main()
