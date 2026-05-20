import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    for i, flow in enumerate(flows):
        url = flow.get("url", "")
        if "create-bet" in url or "bet-request" in url or "bet6" in url:
            print(f"Flow [{i}]: {flow.get('method')} {url}")

if __name__ == "__main__":
    main()
