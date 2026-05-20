import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Betnacional client."""
    
    CPF: str = os.getenv("BETNACIONAL_CPF", "")
    PASSWORD: str = os.getenv("BETNACIONAL_PASSWORD", "")
    
    # Base URL of Betnacional
    BASE_URL: str = os.getenv("BETNACIONAL_BASE_URL", "https://betnacional.bet.br")
    
    # API endpoints (to be verified via proxy capture)
    LOGIN_ENDPOINT: str = os.getenv("BETNACIONAL_LOGIN_ENDPOINT", "/api/v1/auth/login") # default fallback
    
    # HTTP requests configuration
    TIMEOUT: int = int(os.getenv("BETNACIONAL_TIMEOUT", "30"))
    
    # Proxy config for the client (optional, in case proxies are needed to avoid bans)
    PROXY: str = os.getenv("BETNACIONAL_PROXY", "")

    # Geolocation configurations (used for bet placement to avoid blocks)
    LATITUDE: float = float(os.getenv("BETNACIONAL_LATITUDE", "-20.044535977536334"))
    LONGITUDE: float = float(os.getenv("BETNACIONAL_LONGITUDE", "-41.68838661069125"))
    ACCURACY: int = int(os.getenv("BETNACIONAL_ACCURACY", "137"))

    # Default User Agent to look like a real browser
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    @classmethod
    def validate(cls):
        """Validates that core configuration parameters are set."""
        if not cls.CPF:
            raise ValueError("BETNACIONAL_CPF env variable is not set.")
        if not cls.PASSWORD:
            raise ValueError("BETNACIONAL_PASSWORD env variable is not set.")
