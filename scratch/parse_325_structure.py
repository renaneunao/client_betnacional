import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Root keys:", list(data.keys()))
    if "pageProps" in data:
        page_props = data["pageProps"]
        initial_state = page_props.get("initialState", {})
        print("initialState keys:", list(initial_state.keys()))
        
        for key in ["events", "cache", "api"]:
            val = initial_state.get(key, {})
            print(f"\n=== initialState['{key}'] ===")
            if isinstance(val, dict):
                print(f"Keys: {list(val.keys())[:15]}")
                # Check for nested keys
                for subk in list(val.keys())[:15]:
                    subval = val[subk]
                    if isinstance(subval, dict):
                        print(f"  - {subk} (dict, keys: {list(subval.keys())[:10]})")
                    elif isinstance(subval, list):
                        print(f"  - {subk} (list, size: {len(subval)})")
                    else:
                        print(f"  - {subk} (type: {type(subval).__name__})")
            else:
                print(f"Value: {type(val).__name__}")
                
if __name__ == "__main__":
    main()
