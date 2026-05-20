import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    print("Request keys:", list(flow["request"].keys()))
    print("Response keys:", list(flow["response"].keys()))

if __name__ == "__main__":
    main()
