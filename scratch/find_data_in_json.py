import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

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
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Search for São Paulo or Flamengo
    search_terms = ["São Paulo", "Flamengo", "Mirassol"]
    
    for term in search_terms:
        print(f"\nSearching for '{term}':")
        matches = find_path(data, term)
        print(f"Found {len(matches)} matches.")
        for path, match_type, val in matches[:10]:
            print(f" - Path: {path} ({match_type})")
            print(f"   Value: {str(val)[:200]}")

if __name__ == "__main__":
    main()
