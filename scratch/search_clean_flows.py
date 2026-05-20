import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    print("Filter: Only Betnacional/bet6 domains, excluding static files & auth/flags/container-monitor noise")
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        
        # Exclude trackers and third-parties
        if "betnacional" not in url and "bet6.com.br" not in url:
            continue
            
        # Exclude static/auth/flags/rum/panda noise
        if any(x in url for x in ["/api/auth/", "/v1/allflags", "/container-monitor", "/web-to-server", "cdn-cgi/rum"]):
            continue
            
        print(f"[{idx}] {method} {url} -> Status {status}")
        
        # If it's a GET or POST that might contain matches/odds, check if it's JSON
        resp_json = flow.get("response", {}).get("body_json")
        if resp_json:
            resp_str = json.dumps(resp_json)
            # Print sample keys
            if isinstance(resp_json, dict):
                print(f"   Keys: {list(resp_json.keys())}")
            elif isinstance(resp_json, list):
                print(f"   List of size {len(resp_json)}")
            print(f"   Snippet: {resp_str[:300]}")
            
if __name__ == "__main__":
    main()
