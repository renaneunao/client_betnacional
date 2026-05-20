import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def search_recursive(val, term, path=""):
    results = []
    if isinstance(val, dict):
        for k, v in val.items():
            current_path = f"{path}['{k}']" if path else f"['{k}']"
            if term.lower() in str(k).lower():
                results.append((current_path, "KEY", str(k)))
            results.extend(search_recursive(v, term, current_path))
    elif isinstance(val, list):
        for idx, item in enumerate(val):
            current_path = f"{path}[{idx}]"
            results.extend(search_recursive(item, term, current_path))
    elif isinstance(val, str):
        if term.lower() in val.lower():
            results.append((path, "STRING_VAL", val))
    elif val is not None:
        if term.lower() in str(val).lower():
            results.append((path, "OTHER_VAL", str(val)))
    return results

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Searching for 'Chapecoense':")
    matches = search_recursive(data, "Chapecoense")
    print(f"Found {len(matches)} matches.")
    for path, match_type, val in matches:
        print(f" - Path: {path} ({match_type})")
        print(f"   Value (first 300 chars): {str(val)[:300]}")
        print("-" * 50)

if __name__ == "__main__":
    main()
