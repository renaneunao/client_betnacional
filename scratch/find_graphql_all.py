import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        if "graphql" in url.lower():
            print(f"[{idx}] {flow.get('method')} {url}")
            resp_json = flow.get("response", {}).get("body_json")
            if resp_json:
                print(f"   Response: {json.dumps(resp_json)[:500]}")
            print("-" * 80)

if __name__ == "__main__":
    main()
