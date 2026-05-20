import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    search_terms = ["Chapecoense", "Remo", "Athletico", "Bragantino", "Mirassol"]
    
    for term in search_terms:
        print(f"\nSearching responses for '{term}':")
        found = False
        for idx, flow in enumerate(flows):
            url = flow.get("url", "")
            resp_body_raw = flow.get("response", {}).get("body_raw", "")
            resp_json = flow.get("response", {}).get("body_json")
            
            # Check raw body
            in_raw = term.lower() in resp_body_raw.lower()
            in_json = False
            if resp_json:
                in_json = term.lower() in json.dumps(resp_json).lower()
                
            if in_raw or in_json:
                found = True
                print(f"[{idx}] {flow.get('method')} {url}")
                print(f"   Status: {flow.get('response', {}).get('status_code')}")
                if resp_json:
                    print(f"   JSON Keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'list'}")
                else:
                    print(f"   Raw Body Length: {len(resp_body_raw)}")
        if not found:
            print("No matches found in any flow.")

if __name__ == "__main__":
    main()
