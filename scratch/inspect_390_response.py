import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    resp = flow.get("response", {})
    print(f"Status Code: {resp.get('status_code')}")
    print("Response JSON:")
    print(json.dumps(resp.get("body_json"), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
