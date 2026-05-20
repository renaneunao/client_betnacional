import os
import sys
import logging
from dotenv import load_dotenv

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betnacional.client import BetnacionalClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

def main():
    load_dotenv()
    
    print("=== Phase 3: Simulated Strategy Intelligence (Full List) ===")
    
    # Initialize client (uses headless Playwright scraper under the hood)
    client = BetnacionalClient(headless_scraper=True)
    
    print("\nLogging in...")
    if not client.login():
        print("Login failed.")
        return
        
    print(f"Current Balance: {client.get_balance():.2f} BRL")
    
    # 1. List matches for the upcoming round
    print("\n1. Listing all available matches...")
    all_matches = client.listar_jogos_rodada_brasileirao()
    
    print(f"\nTotal matches found: {len(all_matches)}")
    print(f"{'Index':<6} | {'ID':<10} | {'Match':<45} | {'Date':<12} | {'Odds (1/X/2)':<20}")
    print("-" * 103)
    for idx, m in enumerate(all_matches):
        home_odd = "-"
        draw_odd = "-"
        away_odd = "-"
        for market in m.markets:
            if market.id == "1":
                for outcome in market.outcomes:
                    if outcome.id == "1":
                        home_odd = f"{outcome.value:.2f}"
                    elif outcome.id == "2":
                        draw_odd = f"{outcome.value:.2f}"
                    elif outcome.id == "3":
                        away_odd = f"{outcome.value:.2f}"
        odds_str = f"{home_odd} / {draw_odd} / {away_odd}"
        match_name = f"{m.home_team} vs {m.away_team}"
        print(f"{idx:<6} | {m.id:<10} | {match_name:<45} | {m.start_time:<12} | {odds_str:<20}")

    if len(all_matches) < 5:
        print("\nNot enough matches found to place a 5-leg parlay.")
        return

    # 2. Simulate Intelligence strategy selection by index (e.g. indexes 0, 2, 4, 6, 8)
    print("\n2. Simulating Intelligence strategy selection by index (0, 2, 4, 6, 8)...")
    selected_indices = [0, 2, 4, 6, 8]
    
    choices = []
    for idx in selected_indices:
        match = all_matches[idx]
        # Alternate choices to make it interesting
        choice = "casa" if idx % 4 == 0 else ("empate" if idx % 4 == 2 else "fora")
        choices.append({
            "match_id": match.id,
            "choice": choice
        })
    
    print("\nStrategy choices to submit:")
    for idx, c in enumerate(choices):
        match = next(m for m in all_matches if m.id == c["match_id"])
        print(f"  Selection #{idx+1} (Index {selected_indices[idx]}): {match.home_team} vs {match.away_team} -> Choice: {c['choice']}")
        
    # 3. Submit parlay using high-level method (we can do a dry run check or a low stake bet)
    # Since we already placed a bet and got 6.00 BRL left, let's run this to verify it resolved correctly.
    # Note: to avoid same-event conflict within 120 seconds, the selected indices use a mix of outcomes.
    print("\n3. Placing Multiple Bet in production...")
    res = client.multipla_rodada_resultados_brasileirao(choices=choices, stake=1.00)
    
    print("\nBet Submission Result:")
    print(f"  - Success: {res.success}")
    print(f"  - Ticket ID: {res.bet_id}")
    print(f"  - Message: {res.message}")
    
    print("\nQuerying updated balance...")
    print(f"Current Balance: {client.get_balance():.2f} BRL")

if __name__ == "__main__":
    main()
