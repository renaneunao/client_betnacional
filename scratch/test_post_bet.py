import time
import requests
from betnacional.client import BetnacionalClient

def main():
    client = BetnacionalClient(headless_scraper=True)
    if not client.login():
        print("Login failed.")
        return
        
    print("Authentication header:")
    print(client.api.session.headers.get("Authorization")[:30] + "...")
    
    # Try a dummy POST request to create-bet using curl_cffi
    url = "https://prod-betnacional-bets.bet6.com.br/api/v1/create-bet"
    payload = {
        "async": 1,
        "bet_type_id": 1,
        "total_stake": 1,
        "location": {"latitude": -20.044, "longitude": -41.688, "accuracy": 137},
        "selections": []
    }
    
    print("\nSending dummy POST via curl_cffi...")
    try:
        t0 = time.time()
        # Call request directly from client api session
        res = client.api.session.post(url, json=payload, timeout=10)
        print(f"Response status: {res.status_code} in {time.time() - t0:.2f}s")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"curl_cffi POST failed: {e}")
        
    print("\nSending dummy POST via standard requests...")
    try:
        # Create standard requests session and copy headers + cookies
        s = requests.Session()
        s.headers.update(client.api.session.headers)
        s.cookies.update(client.api.cookies)
        
        t0 = time.time()
        res = s.post(url, json=payload, timeout=10)
        print(f"Response status: {res.status_code} in {time.time() - t0:.2f}s")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"standard requests POST failed: {e}")

if __name__ == "__main__":
    main()
