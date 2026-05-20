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
        if "325" in url and "betnacional.bet.br" in url and ".json" not in url:
            if "doubleclick" in url or "facebook" in url or "google" in url or "taboola" in url:
                continue
            print(f"[{idx}] {flow.get('method')} {url}")
            resp_body = flow.get("response", {}).get("body_raw", "")
            print(f"   Status: {flow.get('response', {}).get('status_code')}")
            print(f"   Resp Length: {len(resp_body)}")
            if len(resp_body) > 0:
                print(f"   Snippet: {resp_body[:500]}")
            print("=" * 80)

if __name__ == "__main__":
    main()
