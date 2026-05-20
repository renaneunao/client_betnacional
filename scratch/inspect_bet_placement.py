import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        if "create-bet" in url or "bet-request-status" in url:
            print(f"[{idx}] {flow.get('method')} {url}")
            print(f"   Status: {flow.get('response', {}).get('status_code')}")
            req_headers = flow.get("request", {}).get("headers", {})
            print(f"   Request Headers (Keys): {list(req_headers.keys())}")
            # print Authorization or cookie presence
            print(f"   Authorization Header: {req_headers.get('Authorization') or req_headers.get('authorization')}")
            print(f"   Cookie Header present: {'Cookie' in req_headers or 'cookie' in req_headers}")
            
            req_body = flow.get("request", {}).get("body_json") or flow.get("request", {}).get("body_raw")
            if req_body:
                print(f"   Request Body: {json.dumps(req_body, indent=2)}")
                
            resp_body = flow.get("response", {}).get("body_json") or flow.get("response", {}).get("body_raw")
            if resp_body:
                print(f"   Response Body: {json.dumps(resp_body, indent=2) if isinstance(resp_body, (dict, list)) else str(resp_body)[:1000]}")
            print("=" * 80)

if __name__ == "__main__":
    main()
