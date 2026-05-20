import time
import requests

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

def test_standard_requests():
    print("Testing standard requests...")
    try:
        t0 = time.time()
        # Force IPv4 using a standard session or just a simple get
        r = requests.get("https://prod-betnacional-bets.bet6.com.br/api/v1/create-bet", timeout=10)
        print(f"Standard requests response code: {r.status_code} in {time.time() - t0:.2f}s")
    except Exception as e:
        print(f"Standard requests failed: {e}")

def test_curl_cffi():
    if not HAS_CURL_CFFI:
        print("curl_cffi not installed.")
        return
    print("Testing curl_cffi...")
    try:
        t0 = time.time()
        r = curl_requests.get("https://prod-betnacional-bets.bet6.com.br/api/v1/create-bet", impersonate="chrome", timeout=10)
        print(f"curl_cffi response code: {r.status_code} in {time.time() - t0:.2f}s")
    except Exception as e:
        print(f"curl_cffi failed: {e}")

if __name__ == "__main__":
    test_standard_requests()
    print("-" * 50)
    test_curl_cffi()
