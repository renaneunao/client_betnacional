import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")
OUTPUT_LOG = os.path.join("scratch", "analysis_output.txt")

def main():
    if not os.path.exists(FLOWS_FILE):
        print(f"File not found: {FLOWS_FILE}")
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    out_lines = []
    out_lines.append(f"Loaded {len(flows)} flows.\n")
    
    # We want to identify:
    # 1. GraphQL operations related to leagues, odds, or placing bets.
    # 2. POST requests to any bet/wager placing endpoints.
    
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        status = flow.get("response", {}).get("status_code", 0)
        
        # 1. Check for GraphQL queries/mutations
        if "graphql" in url:
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
                out_lines.append(f"[GraphQL] [{method}] {op_name} -> Status {status}")
                # Print details if it seems related to placing a bet or loading sports
                if any(x in op_name.lower() for x in ["bet", "wager", "place", "fixture", "market", "championship", "league", "event", "sport", "championship"]):
                    out_lines.append(f"  URL: {url}")
                    if req_body_json:
                        out_lines.append(f"  Req Body: {json.dumps(req_body_json)}")
                    resp_json = flow.get("response", {}).get("body_json")
                    if resp_json:
                        out_lines.append(f"  Resp Body (truncated): {json.dumps(resp_json)[:1500]}")
                    out_lines.append("")
        
        # 2. Check for other POST requests (e.g. REST API endpoints)
        elif method == "POST" and "container-monitor" not in url and "log" not in url and "analytics" not in url and "collect" not in url:
            out_lines.append(f"[REST POST] {url} -> Status {status}")
            req_body_json = flow.get("request", {}).get("body_json") or flow.get("request", {}).get("body_raw")
            out_lines.append(f"  Req Body: {req_body_json}")
            resp_body = flow.get("response", {}).get("body_json") or flow.get("response", {}).get("body_raw")
            out_lines.append(f"  Resp Body: {str(resp_body)[:1500]}")
            out_lines.append("")

    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
    print(f"Analysis saved to {OUTPUT_LOG}")

if __name__ == "__main__":
    main()
