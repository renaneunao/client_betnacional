import logging
import os
import sys
from dotenv import load_dotenv

# Ensure the parent directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betnacional.client import BetnacionalClient
from betnacional.models.bet import BetSelection

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

def main():
    load_dotenv()
    
    print("=" * 70)
    print(" Betnacional Championship Scraping & Betting Integration Example")
    print("=" * 70)
    
    # Initialize the Betnacional Client
    # Set headless_scraper=True to run Chrome in background (headless)
    client = BetnacionalClient(headless_scraper=True)
    
    # Step 1: Perform login
    print("\n[Step 1] Logging into Betnacional...")
    try:
        if client.login():
            print("Login successful!")
        else:
            print("Login failed.")
            return
    except Exception as e:
        print(f"Error during login: {e}")
        return
        
    # Step 2: Fetch and verify account balance
    print("\n[Step 2] Fetching account profile and balance...")
    try:
        profile = client.get_profile()
        print(f"User Profile details:")
        print(f"  - Customer ID: {profile.id}")
        print(f"  - Username/CPF: {profile.username}")
        print(f"  - Account Balance: {profile.balance:.2f} {profile.currency}")
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return

    # Step 3: Scrape matches and odds for Brasileirão Série A (tournamentId = 325)
    print("\n[Step 3] Scraping Brasileirão Série A matches & odds (Tournament ID: 325)...")
    try:
        matches = client.get_championship_matches(325)
        print(f"Found {len(matches)} upcoming matches:")
        
        for idx, match in enumerate(matches):
            print(f"\n  Match #{idx+1}: {match.home_team} vs {match.away_team}")
            print(f"    - ID: {match.id}")
            print(f"    - Start Time: {match.start_time}")
            for market in match.markets:
                print(f"    - Market: {market.name}")
                for outcome in market.outcomes:
                    print(f"      * [{outcome.id}] {outcome.name}: {outcome.value}")
    except Exception as e:
        print(f"Error scraping matches: {e}")
        return

    # Step 4: Placing a bet (Simulated / Safety Notice)
    print("\n[Step 4] Bet Placement Demonstration")
    if not matches:
        print("No matches available to simulate betting.")
        return
        
    first_match = matches[0]
    # Let's target the Home team win
    market_id = "1" # Resultado Final
    outcome_id = "1" # Home Team
    
    # Find the corresponding outcome details
    home_outcome = None
    for market in first_match.markets:
        if market.id == market_id:
            for outcome in market.outcomes:
                if outcome.id == outcome_id:
                    home_outcome = outcome
                    break
                    
    if not home_outcome:
        print("Could not find the target outcome in the first match.")
        return
        
    print(f"Selected Outcome details:")
    print(f"  - Match: {first_match.home_team} vs {first_match.away_team} (ID: {first_match.id})")
    print(f"  - Selection: {home_outcome.name} Win (Outcome ID: {outcome_id})")
    print(f"  - Current Odd: {home_outcome.value}")
    print(f"  - Target Stake: 1.00 BRL (Minimum Stake)")
    
    print("\n[SAFETY NOTICE] To avoid placing real money bets automatically during tests,")
    print("the bet placement code is commented out below. To place a real bet, uncomment")
    print("the code in examples/betting_example.py and re-run.")
    
    # To place a real single bet:
    # try:
    #     print("\nPlacing a real single bet of 1.00 BRL...")
    #     res = client.place_bet(
    #         match_id=first_match.id,
    #         market_id=market_id,
    #         outcome_id=outcome_id,
    #         odd_value=home_outcome.value,
    #         stake=1.00
    #     )
    #     print(f"Bet Response success: {res.success}")
    #     print(f"Ticket ID / Bet ID: {res.bet_id}")
    #     print(f"Message: {res.message}")
    #     if res.balance_after is not None:
    #         print(f"Balance After: {res.balance_after:.2f} BRL")
    # except Exception as e:
    #     print(f"Error placing bet: {e}")

    # To place a real multiple/parlay bet (e.g. first 2 matches, home win on both):
    # if len(matches) >= 2:
    #     sel1 = BetSelection(match_id=matches[0].id, market_id="1", outcome_id="1", odd_value=matches[0].markets[0].outcomes[0].value)
    #     sel2 = BetSelection(match_id=matches[1].id, market_id="1", outcome_id="1", odd_value=matches[1].markets[0].outcomes[0].value)
    #     try:
    #         print("\nPlacing a real multiple bet of 1.00 BRL on two matches...")
    #         res = client.place_multi_bet(selections=[sel1, sel2], stake=1.00)
    #         print(f"Multiple Bet Response success: {res.success}")
    #         print(f"Ticket ID / Bet ID: {res.bet_id}")
    #         print(f"Message: {res.message}")
    #     except Exception as e:
    #         print(f"Error placing multiple bet: {e}")

if __name__ == "__main__":
    main()
