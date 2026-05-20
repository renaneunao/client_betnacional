import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    # Let's search for next/data, graphql, or fixtures anywhere
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        
        # Check if URL contains next/data, graphql, or api/v1/sports or fixtures
        if any(x in url.lower() for x in ["next/data", "graphql", "fixtures", "market", "odds", "sport", "championship", "events"]):
            if "doubleclick" in url or "facebook" in url or "google" in url or "taboola" in url or "advcake" in url:
                continue
            print(f"[{idx}] {method} {url} -> Status {status}")
            req_body = flow.get("request", {}).get("body_json") or flow.get("request", {}).get("body_raw")
            if req_body:
                print(f"   Req Body: {str(req_body)[:300]}")
            resp_json = flow.get("response", {}).get("body_json")
            if resp_json:
                print(f"   Resp type: {type(resp_json)}")
                if isinstance(resp_json, dict):
                    print(f"   Resp Keys: {list(resp_json.keys())}")
                elif isinstance(resp_json, list):
                    print(f"   Resp List size: {len(resp_json)}")
            else:
                resp_raw = flow.get("response", {}).get("body_raw") or ""
                print(f"   Resp Raw Length: {len(resp_raw)}")
            print("-" * 100)

if __name__ == "__main__":
    main()
