import logging
from typing import Dict, Any, Optional
from betnacional.config import Config
from betnacional.exceptions import HTTPError, NetworkError

logger = logging.getLogger("betnacional.api")

# Try importing curl_cffi for Cloudflare bypass. Fallback to requests if import fails.
try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
    logger.info("Using curl_cffi for browser impersonation (stealth bypass).")
except ImportError:
    import requests as normal_requests
    HAS_CURL_CFFI = False
    logger.warning("curl_cffi not installed. Falling back to standard requests (higher risk of Cloudflare block).")

class BaseAPIClient:
    """Low-level API client managing cookies, headers, and HTTP request routing."""
    
    def __init__(self, impersonate_browser: str = "chrome"):
        self.base_url = Config.BASE_URL.rstrip("/")
        self.headers = {
            "User-Agent": Config.DEFAULT_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": self.base_url + "/",
            "Origin": self.base_url,
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        # Initialize session
        if HAS_CURL_CFFI:
            # curl_cffi session with Chrome impersonation
            self.session = curl_requests.Session(impersonate=impersonate_browser)
        else:
            # standard requests session
            self.session = normal_requests.Session()

        # Apply default headers to session
        self.session.headers.update(self.headers)
        
        # Set proxy if configured
        if Config.PROXY:
            proxies = {
                "http": Config.PROXY,
                "https": Config.PROXY
            }
            self.session.proxies = proxies

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        return_raw_response: bool = False,
        **kwargs
    ) -> Any:
        """Sends an HTTP request and returns the parsed JSON response, raw content, or Response object."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            url = endpoint
        else:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
        timeout = timeout or Config.TIMEOUT
        
        # Merge call-specific headers
        req_headers = headers or {}

        logger.debug("Request: %s %s | Params: %s | Headers: %s", method, url, params, req_headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=req_headers,
                timeout=timeout,
                **kwargs
            )
        except Exception as e:
            logger.error("Network error during request to %s: %s", url, e)
            raise NetworkError(f"Failed to connect to Betnacional: {e}") from e

        logger.debug("Response: Status %d | Body (truncated): %s", response.status_code, response.text[:500])

        # If raw response requested, return it directly
        if return_raw_response:
            return response

        # Handle HTTP Errors
        if not response.ok:
            # Check for Cloudflare Turnstile block / security wall
            if response.status_code in [403, 503] and "cloudflare" in response.text.lower():
                raise HTTPError(
                    "Cloudflare security block triggered. Captcha or JS challenge required.",
                    status_code=response.status_code,
                    response_text=response.text
                )
            
            raise HTTPError(
                f"HTTP Request failed with status {response.status_code}",
                status_code=response.status_code,
                response_text=response.text
            )

        # Parse JSON
        try:
            return response.json()
        except ValueError:
            # Return raw text if not JSON
            return response.text

    def get(self, endpoint: str, **kwargs) -> Any:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Any:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Any:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Any:
        return self.request("DELETE", endpoint, **kwargs)

    @property
    def cookies(self) -> Dict[str, str]:
        """Returns session cookies as a dictionary."""
        if HAS_CURL_CFFI:
            # curl_cffi session cookies access
            return self.session.cookies.get_dict()
        else:
            return self.session.cookies.get_dict()
            
    def update_cookies(self, cookies: Dict[str, str]):
        """Manually update session cookies."""
        for name, value in cookies.items():
            self.session.cookies.set(name, value)
