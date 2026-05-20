import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cache = data["pageProps"]["initialState"]["cache"]
    print("cache keys:", list(cache.keys()))
    
    for k in cache.keys():
        print(f"cache['{k}'] keys:", list(cache[k].keys()))
        if "entities" in cache[k]:
            entities = cache[k]["entities"]
            print(f"  entities type: {type(entities)}, size: {len(entities)}")
            if len(entities) > 0:
                print(f"  first 3 keys of entities: {list(entities.keys())[:3]}")

if __name__ == "__main__":
    main()
