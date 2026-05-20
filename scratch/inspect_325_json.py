import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")
OUTPUT_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    # Flow 226 has the JSON
    flow = flows[226]
    resp_json = flow.get("response", {}).get("body_json")
    
    if resp_json:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(resp_json, f, indent=2, ensure_ascii=False)
        print(f"Dumped JSON data to {OUTPUT_FILE}")
    else:
        print("Flow 226 did not contain body_json.")

if __name__ == "__main__":
    main()
