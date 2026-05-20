import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    print("Flow 390 Request Body:")
    print(json.dumps(flow["request"]["body_json"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
