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
    for i in range(min(10, len(flows))):
        flow = flows[i]
        req = flow.get("request", {})
        print(f"Flow [{i}]: {req.get('method')} {req.get('url')}")

if __name__ == "__main__":
    main()
