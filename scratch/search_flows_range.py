import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    start = 200
    end = 240
    for idx in range(start, min(end, len(flows))):
        flow = flows[idx]
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        print(f"[{idx}] {method} {url} -> Status {status}")

if __name__ == "__main__":
    main()
