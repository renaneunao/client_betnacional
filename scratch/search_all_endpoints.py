import json
import os
from urllib.parse import urlparse

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    endpoints = {}
    
    for flow in flows:
        url = flow.get("url", "")
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        method = flow.get("method", "GET")
        
        # Filter to keep only betnacional or related bet6 domains
        if "betnacional" not in domain and "bet6" not in domain:
            continue
            
        key = (method, domain, path)
        if key not in endpoints:
            endpoints[key] = {
                "count": 0,
                "example_url": url,
                "flow": flow
            }
        endpoints[key]["count"] += 1
        
    print(f"Total unique Betnacional endpoints: {len(endpoints)}")
    print("\n--- Endpoints List ---")
    for key, info in sorted(endpoints.items(), key=lambda x: (x[0][1], x[0][2])):
        method, domain, path = key
        print(f"[{method}] {domain}{path} (Called {info['count']} times)")
        
        # Check request body/params for interesting stuff
        flow = info["flow"]
        req_body = flow.get("request", {}).get("body_json") or flow.get("request", {}).get("body_raw")
        if req_body:
            print(f"   Sample Req Body: {str(req_body)[:300]}")
            
        resp_body = flow.get("response", {}).get("body_json") or flow.get("response", {}).get("body_raw")
        if resp_body:
            # Check if it has list of games or sports
            resp_str = str(resp_body)
            print(f"   Sample Resp Body (truncated): {resp_str[:300]}")
        print("-" * 50)

if __name__ == "__main__":
    main()
