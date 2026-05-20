import json
import os
from urllib.parse import urlparse

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    paths = set()
    for flow in flows:
        url = flow.get("url", "")
        parsed = urlparse(url)
        if "betnacional.bet.br" in parsed.netloc:
            paths.add(f"{flow.get('method')} {parsed.path}")

    print("Unique paths on betnacional.bet.br:")
    for p in sorted(paths):
        print(f" - {p}")

if __name__ == "__main__":
    main()
