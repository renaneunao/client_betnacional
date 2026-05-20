class BetnacionalException(Exception):
    """Base exception class for all Betnacional client issues."""
    pass

class ConfigurationError(BetnacionalException):
    """Exception raised when configuration is invalid or missing."""
    pass

class NetworkError(BetnacionalException):
    """Exception raised when a network error occurs during communication with Betnacional."""
    pass

class HTTPError(NetworkError):
    """Exception raised when an HTTP request returns an error status code."""
    def __init__(self, message: str, status_code: int = None, response_text: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class AuthenticationError(BetnacionalException):
    """Exception raised when authentication fails (invalid credentials, captcha, etc.)."""
    pass

class SessionExpiredError(AuthenticationError):
    """Exception raised when the session is expired or invalid."""
    pass

class ChallengeRequiredError(AuthenticationError):
    """Exception raised when Cloudflare challenge or captcha is encountered and cannot be bypassed automatically."""
    pass

class APIError(BetnacionalException):
    """Exception raised when the Betnacional API returns a domain-level error."""
    pass
