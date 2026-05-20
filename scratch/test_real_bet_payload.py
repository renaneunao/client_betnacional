import time
import os
import sys
import logging
from dotenv import load_dotenv

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betnacional.client import BetnacionalClient
from betnacional.models.bet import BetSelection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

def main():
    load_dotenv()
    client = BetnacionalClient(headless_scraper=True)
    
    print("Logging in...")
    if not client.login():
        print("Login failed.")
        return
        
    print("Scraping matches...")
    matches = client.get_championship_matches(325)
    if len(matches) < 5:
        print("Error: not enough matches.")
        return
        
    selections = []
    print("Building selections:")
    for i in range(5):
        match = matches[i]
        home_outcome = None
        for market in match.markets:
            if market.id == "1":
                for outcome in market.outcomes:
                    if outcome.id == "1":
                        home_outcome = outcome
                        break
        
        if not home_outcome:
            print("Home outcome missing.")
            return
            
        print(f"  Match {match.id} ({match.home_team}): odd {home_outcome.value}")
        selections.append({
            "event_id": int(match.id),
            "market_id": 1,
            "odd": home_outcome.value,
            "odd_original": home_outcome.value,
            "odd_percentual": 1,
            "outcome_id": "1",
            "specifier": "",
            "sr_event_odd_id": f"{match.id}_1_1_",
            "stake": None,
            "origin_page": 4,
            "variant": "standard",
            "is_recommendation": False,
            "pi": "radar",
            "selections": []
        })
        
    payload = {
        "async": 1,
        "bet_type_id": 2, # Multiple
        "total_stake": 1.00,
        "channel_id": 0,
        "accept_odd_above": 0,
        "location": {
            "latitude": -20.044535977536334,
            "longitude": -41.68838661069125,
            "accuracy": 137
        },
        "bets": selections
    }
    
    url = "https://prod-betnacional-bets.bet6.com.br/api/v1/create-bet"
    print("\nSending real POST via curl_cffi...")
    try:
        t0 = time.time()
        res = client.api.session.post(url, json=payload, timeout=15)
        print(f"Response status: {res.status_code} in {time.time() - t0:.2f}s")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"curl_cffi POST failed: {e}")

if __name__ == "__main__":
    main()
