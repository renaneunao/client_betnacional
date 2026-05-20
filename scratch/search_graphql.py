import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    graphql_calls = []
    
    for flow in flows:
        url = flow.get("url", "")
        if "graphql" not in url:
            continue
            
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        
        # Determine operation name
        op_name = None
        if "?" in url:
            params = url.split("?")[-1].split("&")
            for p in params:
                if p.startswith("operationName="):
                    op_name = p.split("=")[-1]
        
        req_body_json = flow.get("request", {}).get("body_json")
        if isinstance(req_body_json, dict):
            op_name = req_body_json.get("operationName") or op_name
        elif isinstance(req_body_json, list):
            op_names = [item.get("operationName") for item in req_body_json if isinstance(item, dict)]
            op_name = f"Batch: {', '.join(filter(None, op_names))}"
            
        if op_name:
            graphql_calls.append({
                "op_name": op_name,
                "url": url,
                "req": req_body_json,
                "resp": flow.get("response", {}).get("body_json"),
                "status": status
            })
            
    print(f"Total GraphQL calls: {len(graphql_calls)}")
    print("\n--- Unique Operation Names ---")
    ops = set(c["op_name"] for c in graphql_calls)
    for op in sorted(ops):
        print(f" - {op}")
        
    print("\n--- GraphQL Details ---")
    for c in graphql_calls:
        op = c["op_name"]
        # Skip repetitive balance checks for readability
        if "Balance" in op:
            continue
            
        print("="*60)
        print(f"OP: {op} | Status: {c['status']}")
        print(f"URL: {c['url'][:150]}")
        if c['req']:
            print(f"Request: {json.dumps(c['req'])[:1000]}")
        resp_str = json.dumps(c['resp']) if c['resp'] else ""
        print(f"Response (truncated): {resp_str[:1500]}")

if __name__ == "__main__":
    main()
