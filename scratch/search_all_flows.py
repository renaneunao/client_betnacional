import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        print("Flows file does not exist.")
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    print(f"Total flows: {len(flows)}")
    keywords = ["bet", "ticket", "slip", "request", "status"]
    
    matches = []
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "")
        if any(kw in url.lower() for kw in keywords):
            matches.append((idx, method, url))
            
    print(f"Found {len(matches)} matches:")
    for idx, method, url in matches:
        print(f"  [{idx}] {method} {url}")

if __name__ == "__main__":
    main()
