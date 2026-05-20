import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    keywords = ["Mirassol", "Fluminense", "Vasco", "Bragantino", "Flamengo", "Palmeiras", "Corinthians", "São Paulo"]
    
    for idx, flow in enumerate(flows):
        if idx >= 300:
            break
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        resp_body = flow.get("response", {}).get("body_raw", "")
        
        matched = []
        for kw in keywords:
            if kw.lower() in url.lower() or kw.lower() in resp_body.lower():
                matched.append(kw)
                
        if matched:
            print(f"[{idx}] {method} {url}")
            print(f"   Matched: {matched}")
            resp_json = flow.get("response", {}).get("body_json")
            if resp_json:
                if isinstance(resp_json, dict):
                    print(f"   Keys: {list(resp_json.keys())}")
                    # Print sample data of keys
                    for k in list(resp_json.keys())[:5]:
                        print(f"     {k}: {str(resp_json[k])[:100]}")
                elif isinstance(resp_json, list):
                    print(f"   List of size {len(resp_json)}")
            else:
                print(f"   Resp Length: {len(resp_body)}")
            print("-" * 80)

if __name__ == "__main__":
    main()
