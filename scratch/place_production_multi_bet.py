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
    
    print("Initializing client...")
    client = BetnacionalClient(headless_scraper=True)
    
    print("Logging in...")
    if not client.login():
        print("Login failed.")
        return
        
    print(f"Current Balance before bet: {client.get_balance():.2f} BRL")
    
    print("Scraping upcoming matches...")
    matches = client.get_championship_matches(325)
    
    if len(matches) < 5:
        print(f"Error: Scraped only {len(matches)} matches, need at least 5.")
        return
        
    selections = []
    print("\nSelecting first 5 matches (Legs of Parlay):")
    for i in range(5):
        match = matches[i]
        # Let's find outcome_id="1" (Home team victory)
        home_outcome = None
        for market in match.markets:
            if market.id == "1": # Resultado Final
                for outcome in market.outcomes:
                    if outcome.id == "1":
                        home_outcome = outcome
                        break
        
        if not home_outcome:
            print(f"Error: Could not find home victory outcome for match {match.home_team} vs {match.away_team}")
            return
            
        print(f"  - Leg #{i+1}: {match.home_team} (ID: {match.id}) | Odd: {home_outcome.value}")
        
        selections.append(BetSelection(
            match_id=match.id,
            market_id="1",
            outcome_id="1",
            odd_value=home_outcome.value
        ))
        
    print("\nSubmitting Multiple Bet of 1.00 BRL in production...")
    res = client.place_multi_bet(selections=selections, stake=1.00)
    
    print("\nBet Submission Result:")
    print(f"  - Success: {res.success}")
    print(f"  - Ticket ID: {res.bet_id}")
    print(f"  - Message: {res.message}")
    
    print("\nQuerying updated balance...")
    print(f"Current Balance after bet: {client.get_balance():.2f} BRL")

if __name__ == "__main__":
    main()
