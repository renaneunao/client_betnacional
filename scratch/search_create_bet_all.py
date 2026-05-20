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
        if "create-bet" in url:
            print(f"Flow [{idx}] {flow.get('method')} {url}")
            req_body = flow.get("request", {}).get("body_json")
            if req_body:
                print(f"   async: {req_body.get('async')}")
                print(f"   bet_type_id: {req_body.get('bet_type_id')}")
                print(f"   total_stake: {req_body.get('total_stake')}")
                print(f"   location: {req_body.get('location')}")
                print(f"   Number of selections: {len(req_body.get('bets', []))}")
                # Print first selection
                if req_body.get('bets'):
                    print(f"   First selection: {req_body['bets'][0]}")
            print("-" * 50)

if __name__ == "__main__":
    main()
