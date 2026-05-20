import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    headers = flow.get("request", {}).get("headers", {})
    print("All Request Headers of Flow 390:")
    for k, v in headers.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
