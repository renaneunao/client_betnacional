import logging
from typing import Dict, Any, Optional
from betnacional.config import Config
from betnacional.exceptions import AuthenticationError, HTTPError

logger = logging.getLogger("betnacional.auth")

class Authenticator:
    """Handles login, token management, and session state validation."""
    
    def __init__(self, api_client):
        self.api = api_client
        self.is_authenticated = False
        self.user_profile: Optional[Dict[str, Any]] = None
        self.access_token: Optional[str] = None

    def login(self, cpf: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Performs authentication against the Betnacional Keycloak and NextAuth server.
        If cpf and password are not passed, loads them from Config.
        """
        import re
        from urllib.parse import urljoin
        
        username = cpf or Config.CPF
        secret = password or Config.PASSWORD

        if not username or not secret:
            raise AuthenticationError("CPF and password must be configured or passed directly.")

        logger.info("Attempting programmatic login for CPF: %s...", username[:3] + "***" + username[-3:])

        try:
            # Step 1: Fetch NextAuth CSRF Token
            logger.info("Step 1/6: Fetching CSRF Token...")
            csrf_res = self.api.get("/api/auth/csrf")
            if not isinstance(csrf_res, dict) or "csrfToken" not in csrf_res:
                raise AuthenticationError(f"Failed to fetch CSRF token. Response: {csrf_res}")
            
            csrf_token = csrf_res["csrfToken"]
            
            # Step 2: Signin initiation
            logger.info("Step 2/6: Initiating NextAuth keycloak signin...")
            signin_payload = {
                "callbackUrl": self.api.base_url + "/",
                "csrfToken": csrf_token,
                "json": "true"
            }
            signin_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": self.api.base_url + "/"
            }
            
            signin_res = self.api.post(
                "/api/auth/signin/keycloak?",
                data=signin_payload,
                headers=signin_headers
            )
            if not isinstance(signin_res, dict) or "url" not in signin_res:
                raise AuthenticationError(f"Failed to initiate signin. Response: {signin_res}")
                
            keycloak_auth_url = signin_res["url"]
            
            # Step 3: Access Keycloak Auth Page and extract action
            logger.info("Step 3/6: Fetching Keycloak login form action...")
            keycloak_page = self.api.get(keycloak_auth_url)
            if not isinstance(keycloak_page, str):
                raise AuthenticationError("Keycloak login page did not return expected HTML structure.")
                
            match = re.search(r'"loginAction"\s*:\s*"([^"]+)"', keycloak_page)
            if not match:
                raise AuthenticationError("Could not locate loginAction URL inside Keycloak page context.")
                
            form_action = match.group(1)
            # Handle possible unicode escapes
            if '\\' in form_action:
                form_action = form_action.encode().decode('unicode-escape')
                
            # Step 4: Submit credentials to Keycloak and follow redirections
            logger.info("Step 4/6: Posting credentials and tracing redirects...")
            login_payload = {
                "username": username,
                "password": secret,
                "MFA_TOKEN": ""
            }
            login_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://auth.betnacional.bet.br",
                "Referer": keycloak_auth_url
            }
            
            # Perform POST but do NOT auto-follow redirects
            res = self.api.post(
                form_action,
                data=login_payload,
                headers=login_headers,
                return_raw_response=True,
                allow_redirects=False
            )
            
            # Follow redirect chain manually
            steps = 0
            current_res = res
            while current_res.status_code in [301, 302, 303, 307, 308] and steps < 10:
                steps += 1
                next_url = current_res.headers.get('location') or current_res.headers.get('Location')
                if not next_url:
                    break
                next_url = urljoin(current_res.url, next_url)
                
                if "required-action" in next_url and "MFA" in next_url:
                    raise AuthenticationError(
                        "MFA_REQUIRED: Autenticacao de 2 fatores detectada (NSX-MFA). "
                        "Use login_interactive() para completar o login no navegador."
                    )
                
                logger.debug("Redirect %d: %s -> %s", steps, current_res.url, next_url)
                current_res = self.api.get(
                    next_url,
                    headers={"Referer": current_res.url},
                    return_raw_response=True,
                    allow_redirects=False
                )

            # Step 5: Fetch NextAuth session to retrieve JWT accessToken
            logger.info("Step 5/6: Fetching NextAuth session access token...")
            session_data = self.api.get("/api/auth/session")
            if not isinstance(session_data, dict) or "accessToken" not in session_data:
                raise AuthenticationError("Failed to fetch session. Please verify credentials or security challenges.")
                
            self.access_token = session_data["accessToken"]
            self.user_profile = session_data.get("nsxUser") or session_data.get("user")
            
            # Step 6: Update session headers with Authorization token for subsequent GraphQL API calls
            logger.info("Step 6/6: Activating authentication session.")
            self.api.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "nsx-token-version": "v2",
                "x-app-client-name": "bet-client",
                "x-app-client-version": "6.26.0"
            })
            
            self.is_authenticated = True
            logger.info("Login completed successfully.")
            return True

        except Exception as e:
            logger.error("Unexpected error during login: %s", e)
            self.is_authenticated = False
            raise AuthenticationError(f"Failed to authenticate: {e}") from e

    def get_session_cookies(self) -> Dict[str, str]:
        """Returns the current cookies active in the session."""
        return self.api.cookies

    def restore_session(self, cookies: Dict[str, str]) -> bool:
        """Restores a session using previously saved cookies."""
        logger.info("Attempting to restore session using stored cookies.")
        self.api.update_cookies(cookies)
        
        try:
            # We can verify the restored cookies by checking /api/auth/session
            session_data = self.api.get("/api/auth/session")
            if isinstance(session_data, dict) and session_data.get("accessToken"):
                self.access_token = session_data["accessToken"]
                self.user_profile = session_data.get("nsxUser") or session_data.get("user")
                
                # Re-apply headers
                self.api.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "nsx-token-version": "v2",
                    "x-app-client-name": "bet-client",
                    "x-app-client-version": "6.26.0"
                })
                self.is_authenticated = True
                logger.info("Session restored successfully.")
                return True
            else:
                logger.warning("Restored cookies are invalid or expired.")
                self.is_authenticated = False
                return False
        except Exception as e:
            logger.warning("Could not restore session: %s", e)
            self.is_authenticated = False
            return False
