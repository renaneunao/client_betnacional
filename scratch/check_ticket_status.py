import os
import sys
import json
from dotenv import load_dotenv

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betnacional.client import BetnacionalClient

def main():
    load_dotenv()
    client = BetnacionalClient(headless_scraper=True)
    if not client.login():
        print("Login failed.")
        return
        
    ticket_id = "NSBNAC000146820171779316250168"
    status_url = f"https://prod-betnacional-bets.bet6.com.br/api/v1/bet-request-status/{ticket_id}"
    
    print(f"Checking status for Ticket ID: {ticket_id}...")
    res = client._request("GET", status_url)
    print("Response JSON:")
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
