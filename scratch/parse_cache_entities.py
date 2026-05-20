import json
import os

JSON_FILE = os.path.join("scratch", "325_details.json")

def main():
    if not os.path.exists(JSON_FILE):
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cache = data["pageProps"]["initialState"]["cache"]
    
    events_entities = cache["events"]["entities"]
    outcomes_entities = cache["outcomes"]["entities"]
    
    print(f"Number of events (matches): {len(events_entities)}")
    print(f"Number of outcomes: {len(outcomes_entities)}")
    
    print("\n--- Event Entities (First 3) ---")
    count = 0
    for event_id, event in events_entities.items():
        print(f"Event ID: {event_id}")
        print(json.dumps(event, indent=2, ensure_ascii=False)[:1000])
        print("-" * 50)
        count += 1
        if count >= 3:
            break
            
    print("\n--- Outcome Entities (First 3) ---")
    count = 0
    for outcome_id, outcome in outcomes_entities.items():
        print(f"Outcome ID: {outcome_id}")
        print(json.dumps(outcome, indent=2, ensure_ascii=False)[:1000])
        print("-" * 50)
        count += 1
        if count >= 3:
            break

if __name__ == "__main__":
    main()
