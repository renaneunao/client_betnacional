import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")
OUTPUT_FILE = os.path.join("scratch", "325_output.txt")

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    out_lines = []
    for idx, flow in enumerate(flows):
        url = flow.get("url", "")
        if "325" in url and url.startswith("https://betnacional.bet.br"):
            method = flow.get("method", "GET")
            status = flow.get("response", {}).get("status_code", 0)
            out_lines.append(f"[{idx}] {method} {url} -> Status {status}")
            resp_body = flow.get("response", {}).get("body_raw", "")
            out_lines.append(f"   Resp Length: {len(resp_body)}")
            if len(resp_body) > 0:
                out_lines.append(f"   Snippet (first 1000): {resp_body[:1000]}")
                out_lines.append(f"   Snippet (last 1000): {resp_body[-1000:]}")
            out_lines.append("=" * 80)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
