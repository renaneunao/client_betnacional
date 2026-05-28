import logging
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from betnacional.api import BaseAPIClient
from betnacional.auth import Authenticator
from betnacional.scraper import ChampionshipScraper
from betnacional.parser import DataParser
from betnacional.config import Config
from betnacional.models.auth import UserProfile
from betnacional.models.odds import Match
from betnacional.models.bet import PlaceBetResponse, BetSelection, BetHistoryResponse, BetHistoryItem, BetHistoryEvent

logger = logging.getLogger("betnacional.client")

SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "session.json")

class BetnacionalClient:
    """
    Main facade client for interacting with the Betnacional platform.
    Initializes underlying API connections, handles authentication,
    and formats responses into Pydantic models.
    """
    
    def __init__(self, impersonate_browser: str = "chrome", headless_scraper: bool = True):
        self.api = BaseAPIClient(impersonate_browser=impersonate_browser)
        self.auth = Authenticator(self.api)
        self.parser = DataParser()
        self.scraper = ChampionshipScraper(headless=headless_scraper)
        logger.info("BetnacionalClient initialized.")

    def login(self, cpf: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Authenticates the user using CPF and Password.
        Uses values from environment variables by default.
        """
        return self.auth.login(cpf=cfp, password=password)

    def login_interactive(self) -> bool:
        """
        Opens a real browser window for the user to log in manually.
        Use this when MFA (2-factor authentication) is required.
        After login, saves session tokens to session.json for future automated use.
        """
        from playwright.sync_api import sync_playwright

        logger.info("Starting interactive login (Playwright browser)...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
            context = browser.new_context(
                no_viewport=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            current_url = [""]

            def on_response(response):
                url = response.url
                if "/api/auth/session" in url:
                    try:
                        body = response.json()
                        if body.get("accessToken"):
                            current_url[0] = url
                    except Exception:
                        pass

            page.on("response", on_response)
            page.goto("https://betnacional.bet.br", wait_until="load")

            print()
            print("=" * 60)
            print("  LOGIN INTERATIVO - Complete o login no navegador")
            print("  (incluindo MFA/codigo se necessario)")
            print()
            print("  Feche o navegador quando estiver logado")
            print("=" * 60)
            print()

            while True:
                try:
                    if not browser.is_connected():
                        break
                    page.wait_for_timeout(1000)
                except Exception:
                    break

            time.sleep(2)

            try:
                cookies = context.cookies()
                self.api.update_cookies({c["name"]: c["value"] for c in cookies})
            except Exception as e:
                logger.warning("Could not extract cookies: %s", e)

            session_data = self.api.get("/api/auth/session")
            if isinstance(session_data, dict) and session_data.get("accessToken"):
                self.auth.access_token = session_data["accessToken"]
                self.auth.user_profile = session_data.get("nsxUser") or session_data.get("user")
                self.auth.is_authenticated = True
                self.api.session.headers.update({
                    "Authorization": f"Bearer {self.auth.access_token}",
                    "nsx-token-version": "v2",
                    "x-app-client-name": "bet-client",
                    "x-app-client-version": "6.26.0"
                })
                self._save_session()
                logger.info("Interactive login successful. Session saved.")
                return True

        logger.error("Interactive login failed.")
        return False

    def _save_session(self):
        try:
            data = {
                "cookies": self.api.cookies,
                "access_token": self.auth.access_token,
                "user_profile": self.auth.user_profile
            }
            with open(SESSION_FILE, "w") as f:
                json.dump(data, f)
            logger.info("Session saved to %s", SESSION_FILE)
        except Exception as e:
            logger.warning("Failed to save session: %s", e)

    def _load_session(self) -> bool:
        if not os.path.exists(SESSION_FILE):
            return False
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
            self.api.update_cookies(data.get("cookies", {}))
            session_data = self.api.get("/api/auth/session")
            if isinstance(session_data, dict) and session_data.get("accessToken"):
                self.auth.access_token = session_data["accessToken"]
                self.auth.user_profile = session_data.get("nsxUser") or session_data.get("user")
                self.auth.is_authenticated = True
                self.api.session.headers.update({
                    "Authorization": f"Bearer {self.auth.access_token}",
                    "nsx-token-version": "v2",
                    "x-app-client-name": "bet-client",
                    "x-app-client-version": "6.26.0"
                })
                logger.info("Session loaded from %s", SESSION_FILE)
                return True
            logger.info("Saved session expired, removing %s", SESSION_FILE)
            os.remove(SESSION_FILE)
        except Exception as e:
            logger.warning("Failed to load session: %s", e)
        return False

    def get_session_cookies(self) -> Dict[str, str]:
        """Retrieves active session cookies to save for later use."""
        return self.auth.get_session_cookies()

    def restore_session(self, cookies: Dict[str, str]) -> bool:
        """Restores a previous session using saved cookies."""
        return self.auth.restore_session(cookies)

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Executes an API request. If the session is expired or unauthenticated,
        it automatically attempts to refresh the session token or perform a full re-login.
        """
        from betnacional.exceptions import HTTPError
        
        if not self.auth.is_authenticated or not self.auth.access_token:
            logger.info("Client is not authenticated. Trying saved session...")
            if self._load_session():
                logger.info("Session restored from file.")
            else:
                logger.info("Executing automatic login...")
                try:
                    self.login()
                except Exception as e:
                    if "MFA" in str(e).upper() or "REQUIRED-ACTION" in str(e).upper():
                        raise RuntimeError(
                            "MFA (autenticacao de 2 fatores) necessaria. "
                            "Use client.login_interactive() para fazer login manual no navegador."
                        ) from e
                    raise
            
        try:
            return self.api.request(method, endpoint, **kwargs)
        except HTTPError as e:
            is_unauthenticated = (e.status_code == 401) or \
                                 (e.status_code == 400 and isinstance(e.response_text, str) and "UNAUTHENTICATED" in e.response_text)
                                 
            if is_unauthenticated:
                logger.info("Session token expired or unauthenticated. Attempting automatic token refresh...")
                # Attempt to renew JWT token using NextAuth cookies
                if self.auth.restore_session(self.auth.get_session_cookies()):
                    logger.info("Session token refreshed successfully. Retrying request...")
                    return self.api.request(method, endpoint, **kwargs)
                else:
                    logger.info("Automatic refresh failed. Attempting full re-login with credentials...")
                    if self.login():
                        logger.info("Re-login successful. Retrying request...")
                        return self.api.request(method, endpoint, **kwargs)
            # Re-raise error if refresh and re-login failed
            raise e

    def get_profile(self) -> UserProfile:
        """
        Retrieves the authenticated user's profile information, 
        including account balances via GraphQL.
        """
        gql_endpoint = "/graphql?operationName=useBalanceQuery&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22421b4800cdd88e2ad88496cf6e2fd48539ae9d20d2782d50fe8ddb159ff0e549%22%7D%7D"
        raw_gql = self._request("GET", gql_endpoint)
        gql_profile = self.parser.parse_user_profile(raw_gql)
        
        # Merge details from next-auth session object if available
        if self.auth.user_profile:
            cached = self.parser.parse_user_profile(self.auth.user_profile)
            gql_profile.name = cached.name or gql_profile.name
            gql_profile.username = cached.username or gql_profile.username
            gql_profile.cpf = cached.cpf or gql_profile.cpf
            if cached.id:
                gql_profile.id = cached.id
                
        return gql_profile

    def get_balance(self) -> float:
        """Helper method to quickly retrieve the user's balance."""
        profile = self.get_profile()
        return profile.balance

    def get_bet_history(
        self,
        status: str = "pending",
        date_start: str = None,
        date_end: str = None,
        limit: int = 20,
        pagination_direction: str = "next"
    ) -> BetHistoryResponse:
        """
        Retrieves the user's bet history from the platform.

        Args:
            status: "pending" for open bets, "completed" for settled bets.
            date_start: Start date in YYYY-MM-DD format.
            date_end: End date in YYYY-MM-DD format.
            limit: Number of records per page.
            pagination_direction: Pagination direction ("next").

        Returns:
            BetHistoryResponse containing bets, events, and scores.
        """
        from datetime import date as dt_date, timedelta

        if date_start is None:
            date_start = (dt_date.today() - timedelta(days=30)).isoformat()
        if date_end is None:
            date_end = dt_date.today().isoformat()

        endpoint = "/api/v2/pending-bets" if status == "pending" else "/api/v2/settled-bets"
        params = (
            f"?status={'pending' if status == 'pending' else 'completed'}"
            f"&paginationDirection={pagination_direction}"
            f"&limit={limit}"
            f"&date_start={date_start}"
            f"&date_end={date_end}"
            f"&startDate={date_start}"
            f"&endDate={date_end}"
        )

        base = "https://prod-betnacional-bets.bet6.com.br"
        url = f"{base}{endpoint}{params}"

        raw = self._request("GET", url)
        return BetHistoryResponse(
            bets=[BetHistoryItem(**b) for b in raw.get("bets", [])],
            events=[BetHistoryEvent(**e) for e in raw.get("events", [])],
            scores=raw.get("scores", [])
        )

    def get_bet_details(self, ticket_id: str) -> dict:
        """
        Retrieves detailed information about a specific ticket, grouped by ticket_id.

        Args:
            ticket_id: The ticket ID (e.g., "NSBNAC000146820171779306048382").

        Returns:
            Dict with 'ticket_id', 'header_id', 'stake', 'total_odd', 'potential_return',
            'status', 'cashout_available', 'created_at', 'selections' (list of per-match details),
            and 'raw_selections' (raw API data for cashout payload construction).
        """
        from datetime import date as dt_date, timedelta

        date_start = (dt_date.today() - timedelta(days=30)).isoformat()
        date_end = dt_date.today().isoformat()

        endpoint = "/api/v2/pending-bets"
        params = (
            f"?status=pending&paginationDirection=next&limit=50"
            f"&date_start={date_start}&date_end={date_end}"
            f"&startDate={date_start}&endDate={date_end}"
        )

        base = "https://prod-betnacional-bets.bet6.com.br"
        url = f"{base}{endpoint}{params}"
        raw = self._request("GET", url)

        bets = raw.get("bets", [])
        ticket_bets = [b for b in bets if b.get("ticket_id") == ticket_id]

        if not ticket_bets:
            return {"ticket_id": ticket_id, "found": False, "selections": []}

        header = ticket_bets[0]
        selections = []

        cashout_product = 1.0
        for b in ticket_bets:
            prob = b.get("current_probability") or b.get("probabilities") or 0
            if prob > 0:
                cashout_product *= prob

            selections.append({
                "event_id": b.get("event_id"),
                "home": b.get("home"),
                "away": b.get("away"),
                "market_name": b.get("market_name"),
                "outcome_name": b.get("outcome_name"),
                "odd": b.get("odd"),
                "current_odd": b.get("current_odd"),
                "current_probability": prob,
                "sr_event_odd_id": b.get("sr_event_odd_id"),
            })

        stake = float(header.get("header_stake", 0))
        total_odd = float(header.get("total_odd", 0))
        cashout_estimate = round(stake * total_odd * cashout_product, 2)

        return {
            "ticket_id": ticket_id,
            "found": True,
            "header_id": header.get("header_id"),
            "stake": header.get("header_stake"),
            "total_odd": header.get("total_odd"),
            "potential_return": header.get("header_return"),
            "status": header.get("bet_status_name"),
            "cashout_available": header.get("cashout_status") == 1,
            "cashout_estimate": cashout_estimate,
            "created_at": header.get("created_at"),
            "selections": selections,
            "raw_selections": ticket_bets
        }

    def cashout(self, ticket_id: str, total_cashout: float) -> dict:
        """
        Attempts to cash out a specific ticket.

        Args:
            ticket_id: The ticket ID (e.g., "NSBNAC000146820171779316250168").
            total_cashout: The cashout amount to accept (pass 0 to accept any offered amount).

        Returns:
            Dict with 'success', 'message', and optionally 'cashout_amount'.
        """
        details = self.get_bet_details(ticket_id)
        if not details.get("found"):
            return {"success": False, "message": f"Ticket {ticket_id} not found in pending bets."}
        if not details.get("cashout_available"):
            return {"success": False, "message": "Cashout not available for this ticket."}

        raw_selections = details["raw_selections"]
        header_id = details["header_id"]

        payload = {
            "ticket_id": ticket_id,
            "id": header_id,
            "total_cashout": total_cashout,
            "evs": 0,
            "selections": [
                {
                    "return_type_id": s.get("return_type_id"),
                    "event_id": s.get("event_id"),
                    "event_status_id": s.get("event_status_id") or 0,
                    "event_date": s.get("event_date") or "0001-01-01T00:00:00",
                    "sport_id": s.get("sport_id"),
                    "market_id": s.get("market_id"),
                    "cashout_status": s.get("cashout_status") or 1,
                    "probabilities": s.get("current_probability") or s.get("probabilities") or 0,
                    "booked": s.get("booked") or 0,
                    "outcome": str(s.get("outcome_id")),
                    "specifier": s.get("specifier") or "",
                    "odd": s.get("current_odd") or s.get("odd"),
                    "original_odd": s.get("odd"),
                    "signature": s.get("signature"),
                    "signed_at": s.get("signed_at"),
                    "signed_at_ts": s.get("signed_at_ts")
                }
                for s in raw_selections
            ],
            "page": "/bets"
        }

        url = "https://prod-betnacional-bets.bet6.com.br/api/v1/cash-out"
        raw = self._request("POST", url, json_data=payload)

        if isinstance(raw, dict) and raw.get("success"):
            return {
                "success": True,
                "message": "Cashout successful.",
                "cashout_amount": raw.get("cashout_amount") or total_cashout,
                "raw": raw
            }

        return {
            "success": False,
            "message": str(raw),
            "raw": raw
        }

    def get_championship_matches(self, tournament_id: int, league_name: str = "") -> List[Match]:
        """
        Retrieves matches and odds for a specific championship by tournament ID.
        Uses headless Playwright scraping to bypass WebSocket restriction.
        """
        return self.scraper.scrape_championship_matches(tournament_id, league_name)

    def _submit_and_poll_bet(
        self, 
        selections: List[Dict[str, Any]], 
        total_stake: float, 
        bet_type_id: int
    ) -> PlaceBetResponse:
        """
        Sends the bet creation request to the Betnacional API and polls for status completion.
        
        Args:
            selections: Formatted list of selections
            total_stake: Total stake value for the bet
            bet_type_id: 1 for Single, 2 for Multiple
        """
        # Formulate API payload matching captured flow 390
        payload = {
            "async": 1,
            "bet_type_id": bet_type_id,
            "total_stake": total_stake,
            "channel_id": 0,
            "accept_odd_above": 0,
            "location": {
                "latitude": Config.LATITUDE,
                "longitude": Config.LONGITUDE,
                "accuracy": Config.ACCURACY
            },
            "bets": selections
        }
        
        # Bet creation API URL
        create_url = "https://prod-betnacional-bets.bet6.com.br/api/v1/create-bet"
        
        logger.info("Submitting bet to platform: type=%d, selections_count=%d, stake=%.2f", bet_type_id, len(selections), total_stake)
        
        try:
            create_res = self._request("POST", create_url, json_data=payload)
            if not isinstance(create_res, dict) or "ticket_id" not in create_res:
                logger.error("Failed to submit bet. Platform response: %s", create_res)
                return PlaceBetResponse(
                    success=False,
                    message=f"Platform bet creation failed: {create_res}"
                )
                
            ticket_id = create_res["ticket_id"]
            logger.info("Bet submitted successfully. Ticket ID: %s. Polling for status...", ticket_id)
            
            # Status polling loop
            status_url = f"https://prod-betnacional-bets.bet6.com.br/api/v1/bet-request-status/{ticket_id}"
            max_attempts = 15
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                time.sleep(1.0)
                
                status_res = self._request("GET", status_url)
                if not isinstance(status_res, dict):
                    continue
                    
                success_data = status_res.get("success")
                if success_data and success_data.get("ticket_id") == ticket_id:
                    logger.info("Bet successfully accepted by sportsbook! Ticket ID: %s", ticket_id)
                    # Try to fetch new balance after bet placement
                    balance_after = None
                    try:
                        balance_after = self.get_balance()
                    except Exception:
                        pass
                    return PlaceBetResponse(
                        success=True,
                        bet_id=ticket_id,
                        message="Bet accepted successfully.",
                        balance_after=balance_after
                    )
                    
                odds_change = status_res.get("odds_change")
                if odds_change:
                    logger.warning("Bet rejected due to odds change: %s", odds_change)
                    return PlaceBetResponse(
                        success=False,
                        bet_id=ticket_id,
                        message=f"Bet rejected: odds change detected. Details: {odds_change}"
                    )
                    
            logger.warning("Polling timed out for Ticket ID: %s", ticket_id)
            return PlaceBetResponse(
                success=False,
                bet_id=ticket_id,
                message="Polling timed out. Bet status is undetermined."
            )
            
        except Exception as e:
            logger.error("Exception during bet placement: %s", e)
            return PlaceBetResponse(
                success=False,
                message=f"Bet placement error: {e}"
            )

    def place_bet(
        self, 
        match_id: str, 
        market_id: str, 
        outcome_id: str, 
        odd_value: float, 
        stake: float
    ) -> PlaceBetResponse:
        """
        Places a bet on a single outcome.
        
        Args:
            match_id: The target match ID
            market_id: The target market ID (usually "1" for Resultado Final)
            outcome_id: The outcome selection ID ("1" = Home, "2" = Draw, "3" = Away)
            odd_value: The odd value at the time of placing the bet
            stake: The monetary amount of the wager in BRL
        """
        selection = {
            "event_id": int(match_id),
            "market_id": int(market_id),
            "odd": odd_value,
            "odd_original": odd_value,
            "odd_percentual": 1,
            "outcome_id": str(outcome_id),
            "specifier": "",
            "sr_event_odd_id": f"{match_id}_{market_id}_{outcome_id}_",
            "stake": None,
            "origin_page": 4,
            "variant": "standard",
            "is_recommendation": False,
            "pi": "radar",
            "selections": []
        }
        
        return self._submit_and_poll_bet(
            selections=[selection],
            total_stake=stake,
            bet_type_id=1  # 1 represents a Single bet
        )

    def place_multi_bet(
        self,
        selections: List[BetSelection],
        stake: float
    ) -> PlaceBetResponse:
        """
        Places a multiple/parlay bet on several outcomes.
        
        Args:
            selections: List of BetSelection models representing the parlay legs
            stake: Total stake value for the parlay bet
        """
        formatted_selections = []
        for sel in selections:
            formatted_selections.append({
                "event_id": int(sel.match_id),
                "market_id": int(sel.market_id),
                "odd": sel.odd_value,
                "odd_original": sel.odd_value,
                "odd_percentual": 1,
                "outcome_id": str(sel.outcome_id),
                "specifier": "",
                "sr_event_odd_id": f"{sel.match_id}_{sel.market_id}_{sel.outcome_id}_",
                "stake": None,
                "origin_page": 4,
                "variant": "standard",
                "is_recommendation": False,
                "pi": "radar",
                "selections": []
            })
            
        return self._submit_and_poll_bet(
            selections=formatted_selections,
            total_stake=stake,
            bet_type_id=2  # 2 represents a Multiple bet
        )

    def listar_jogos_rodada_brasileirao(self, tournament_id: int = 325, league_name: str = "") -> List[Match]:
        """
        Lists all upcoming Brasileirão matches available on the platform sorted chronologically.
        
        Args:
            tournament_id: 325 for Série A, 390 for Série B.
            league_name: Display name for the league.
        """
        league = league_name or ("Brasileirão Série A" if tournament_id == 325 else f"Torneio {tournament_id}")
        logger.info("Fetching all available %s matches (ID: %d)...", league, tournament_id)
        matches = self.get_championship_matches(tournament_id, league)

        def get_match_date(m: Match) -> datetime:
            if not m.start_time:
                return datetime.max
            try:
                date_part = m.start_time.split()[0]
                return datetime.strptime(date_part, "%d/%m/%Y")
            except Exception:
                return datetime.max

        matches.sort(key=get_match_date)
        return matches

    def listar_jogos_rodada_brasileirao_serie_b(self) -> List[Match]:
        """Lists all upcoming Brasileirão Série B matches sorted chronologically."""
        return self.listar_jogos_rodada_brasileirao(tournament_id=390, league_name="Brasileirão Série B")

    def multipla_rodada_resultados_brasileirao(
        self,
        choices: List[Dict[str, str]],
        stake: float,
        tournament_id: int = 325
    ) -> PlaceBetResponse:
        """
        Places a parlay/multiple bet using high-level choices.
        
        Args:
            choices: List of selections: [{"match_id": "...", "choice": "casa" | "empate" | "fora"}]
            stake: Total stake value in BRL
            tournament_id: 325 for Série A, 390 for Série B.
        """
        logger.info("Placing parlay bet of %.2f BRL for %d selections (tournament %d)...", stake, len(choices), tournament_id)
        
        current_matches = self.get_championship_matches(tournament_id)
        match_lookup = {m.id: m for m in current_matches}
        
        # Map human-readable choice to outcome IDs
        choice_mapping = {
            "casa": "1",
            "empate": "2",
            "fora": "3"
        }
        
        selections = []
        for index, item in enumerate(choices):
            match_id = str(item.get("match_id", ""))
            choice = item.get("choice", "").lower()
            
            if match_id not in match_lookup:
                raise ValueError(f"Match ID {match_id} not found in current Brasileirão matches.")
                
            if choice not in choice_mapping:
                raise ValueError(f"Invalid choice '{choice}'. Must be 'casa', 'empate', or 'fora'.")
                
            match = match_lookup[match_id]
            outcome_id = choice_mapping[choice]
            
            # Locate the outcome in the first market (Resultado Final / market_id='1')
            odd_value = None
            target_market_id = "1"
            
            for market in match.markets:
                if market.id == target_market_id:
                    for outcome in market.outcomes:
                        if outcome.id == outcome_id:
                            odd_value = outcome.value
                            break
                            
            if odd_value is None:
                raise ValueError(f"Could not locate outcome '{choice}' (ID: {outcome_id}) in match {match.home_team} vs {match.away_team}.")
                
            logger.info("Resolved selection #%d: Match %s vs %s | Choice=%s | Current Odd=%.2f",
                        index + 1, match.home_team, match.away_team, choice, odd_value)
                        
            selections.append(BetSelection(
                match_id=match_id,
                market_id=target_market_id,
                outcome_id=outcome_id,
                odd_value=odd_value
            ))
            
        return self.place_multi_bet(selections=selections, stake=stake)
