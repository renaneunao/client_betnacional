import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")
OUTPUT_FILE = os.path.join("scratch", "leagues_output.txt")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    # Let's search for keywords like team names
    keywords = ["Mirassol", "Fluminense", "Vasco", "Bragantino", "Flamengo", "Palmeiras", "Corinthians", "brasileirao", "championship"]
    
    out_lines = []
    found_count = 0
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        method = flow.get("method", "GET")
        resp_body = flow.get("response", {}).get("body_raw", "")
        
        # Check if URL or response text contains any keyword
        matched = []
        for kw in keywords:
            if kw.lower() in url.lower() or kw.lower() in resp_body.lower():
                matched.append(kw)
                
        if matched:
            found_count += 1
            out_lines.append(f"[{idx}] {method} {url} (Matched: {', '.join(matched)})")
            # If it's a JSON response, print keys
            resp_json = flow.get("response", {}).get("body_json")
            if isinstance(resp_json, dict):
                out_lines.append(f"   Response JSON keys: {list(resp_json.keys())}")
                out_lines.append(f"   Sample JSON: {json.dumps(resp_json)[:2000]}")
            elif isinstance(resp_json, list):
                out_lines.append(f"   Response JSON list of size {len(resp_json)}")
                if len(resp_json) > 0:
                    out_lines.append(f"   Sample list item: {json.dumps(resp_json[0])[:2000]}")
            else:
                out_lines.append(f"   Response raw (first 1000 chars): {resp_body[:1000]}")
            out_lines.append("-" * 80)
            
    out_lines.append(f"Total matched flows: {found_count}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"Saved matched flows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
