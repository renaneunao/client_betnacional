import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    flow = flows[390]
    print("Flow 390 keys:", list(flow.keys()))
    print("Server connection IP address details:")
    print("  - client_conn:", flow.get("client_conn"))
    print("  - server_conn:", flow.get("server_conn"))

if __name__ == "__main__":
    main()
