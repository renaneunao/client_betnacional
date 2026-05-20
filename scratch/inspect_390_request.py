import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    req_body = flow.get("request", {}).get("body_json")
    print("Full Request Body of flow 390:")
    print(json.dumps(req_body, indent=2))

if __name__ == "__main__":
    main()
