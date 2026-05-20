import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    term = "Chapecoense"
    print(f"Searching all flows for '{term}':")
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        req_raw = flow.get("request", {}).get("body_raw", "")
        req_json = flow.get("request", {}).get("body_json")
        resp_raw = flow.get("response", {}).get("body_raw", "")
        resp_json = flow.get("response", {}).get("body_json")
        
        found = False
        if term.lower() in url.lower():
            found = True
        elif term.lower() in req_raw.lower():
            found = True
        elif req_json and term.lower() in json.dumps(req_json).lower():
            found = True
        elif term.lower() in resp_raw.lower():
            found = True
        elif resp_json and term.lower() in json.dumps(resp_json).lower():
            found = True
            
        if found:
            print(f"[{idx}] {flow.get('method')} {url}")
            print(f"   Status: {flow.get('response', {}).get('status_code')}")
            # check if it is in request or response
            in_req = (term.lower() in req_raw.lower()) or (req_json and term.lower() in json.dumps(req_json).lower())
            in_resp = (term.lower() in resp_raw.lower()) or (resp_json and term.lower() in json.dumps(resp_json).lower())
            print(f"   In Request: {in_req}, In Response: {in_resp}")
            print("-" * 50)

if __name__ == "__main__":
    main()
