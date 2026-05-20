import json
import os

FLOWS_FILE = os.path.join("mitm_capture", "captured_flows.json")

def find_path(data, search_str, path=""):
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{path}['{k}']" if path else f"['{k}']"
            if search_str.lower() in str(k).lower():
                results.append((current_path, "KEY", str(k)))
            results.extend(find_path(v, search_str, current_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            current_path = f"{path}[{idx}]"
            results.extend(find_path(item, search_str, current_path))
    elif isinstance(data, str):
        if search_str.lower() in data.lower():
            results.append((path, "VALUE", data))
    return results

def main():
    if not os.path.exists(FLOWS_FILE):
        return

    with open(FLOWS_FILE, "r", encoding="utf-8") as f:
        flows = json.load(f)

    data = flows[226]["response"]["body_json"]
    
    print("Searching for 'Botafogo':")
    matches = find_path(data, "Botafogo")
    print(f"Found {len(matches)} matches.")
    for path, match_type, val in matches[:10]:
        print(f" - Path: {path} ({match_type})")
        print(f"   Value: {str(val)[:200]}")

if __name__ == "__main__":
    main()
