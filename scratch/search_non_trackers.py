import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    print("Strict Filter: Business logic endpoints on betnacional or bet6")
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        
        # Exclude tracking and infrastructure noise
        if "betnacional" not in url and "bet6.com.br" not in url:
            continue
        if any(x in url for x in [
            "/api/auth/", "/v1/allflags", "/container-monitor", "/web-to-server", "cdn-cgi/rum",
            "rum", "collect", "analytics", "tracking", "log", "policy-svc", "container-monitor"
        ]):
            continue
            
        print(f"[{idx}] {method} {url} -> Status {status}")
        
        # Print request payload
        req_body = flow.get("request", {}).get("body_json") or flow.get("request", {}).get("body_raw")
        if req_body:
            print(f"   Req Body: {json.dumps(req_body)[:500]}")
            
        # Print response summary
        resp_json = flow.get("response", {}).get("body_json")
        if resp_json:
            print(f"   Resp Keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'list'}")
            print(f"   Resp Body: {json.dumps(resp_json)[:1000]}")
        else:
            resp_raw = flow.get("response", {}).get("body_raw") or ""
            print(f"   Resp Raw Length: {len(resp_raw)}")
            if len(resp_raw) > 0 and status == 200:
                print(f"   Resp Snippet: {resp_raw[:500]}")
        print("=" * 100)

if __name__ == "__main__":
    main()
