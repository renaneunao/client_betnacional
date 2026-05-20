import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Let's inspect data["pageProps"]["initialState"]["events"]
    events_state = data["pageProps"]["initialState"]["events"]
    print("events_state keys:", list(events_state.keys()))
    
    queries = events_state.get("queries", {})
    print("queries keys:")
    for k in queries.keys():
        print(f"  - {k}")
        q_data = queries[k].get("data")
        if q_data:
            print(f"    Data type: {type(q_data)}")
            if isinstance(q_data, dict):
                print(f"    Data keys: {list(q_data.keys())[:10]}")
            elif isinstance(q_data, list):
                print(f"    Data list size: {len(q_data)}")
                if len(q_data) > 0:
                    print(f"    First item sample: {str(q_data[0])[:500]}")

if __name__ == "__main__":
    main()
