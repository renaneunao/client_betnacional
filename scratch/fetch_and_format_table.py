import os
import sys
from dotenv import load_dotenv

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betnacional.client import BetnacionalClient

def main():
    load_dotenv()
    client = BetnacionalClient(headless_scraper=True)
    
    # Login
    if not client.login():
        print("Login failed.")
        return
        
    # Fetch championship matches (tournament ID 325)
    matches = client.get_championship_matches(325)
    
    # Print Markdown Table Header
    print("| Partida | Data | Vitória Casa (1) | Empate (X) | Vitória Fora (2) | ID do Evento |")
    print("| :--- | :--- | :---: | :---: | :---: | :---: |")
    
    for match in matches:
        home_odd = "-"
        draw_odd = "-"
        away_odd = "-"
        
        for market in match.markets:
            if market.id == "1":  # Resultado Final
                for outcome in market.outcomes:
                    if outcome.id == "1":
                        home_odd = f"{outcome.value:.2f}"
                    elif outcome.id == "2":
                        draw_odd = f"{outcome.value:.2f}"
                    elif outcome.id == "3":
                        away_odd = f"{outcome.value:.2f}"
                        
        match_str = f"{match.home_team} vs {match.away_team}"
        print(f"| {match_str} | {match.start_time} | {home_odd} | {draw_odd} | {away_odd} | {match.id} |")

if __name__ == "__main__":
    main()
