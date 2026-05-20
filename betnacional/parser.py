import logging
from typing import Dict, Any, List
from betnacional.models.auth import UserProfile
from betnacional.models.odds import Match, Market, OddOutcome
from betnacional.models.bet import PlaceBetResponse

logger = logging.getLogger("betnacional.parser")

class DataParser:
    """Parses raw HTML or JSON responses from Betnacional into structured Pydantic models."""
    
    @staticmethod
    def parse_user_profile(data: Dict[str, Any]) -> UserProfile:
        """Parses raw user data into UserProfile model."""
        try:
            # Check if this is the GraphQL useBalanceQuery response
            if "data" in data and "viewer" in data["data"]:
                viewer = data["data"]["viewer"]
                if viewer is None:
                    return UserProfile(balance=0.0)
                
                balance_micros = 0
                if "balance" in viewer and "total" in viewer["balance"]:
                    balance_micros = viewer["balance"]["total"].get("micros", 0)
                balance = float(balance_micros) / 1000000.0
                
                raw_id = viewer.get("id")
                numeric_id = None
                if raw_id:
                    if ":" in raw_id:
                        numeric_id = raw_id.split(":")[-1]
                    else:
                        import base64
                        try:
                            decoded = base64.b64decode(raw_id).decode("utf-8")
                            if ":" in decoded:
                                numeric_id = decoded.split(":")[-1]
                        except Exception:
                            numeric_id = raw_id
                
                return UserProfile(
                    id=int(numeric_id) if numeric_id and numeric_id.isdigit() else None,
                    balance=balance,
                    currency="BRL"
                )
            
            # Check if it is a standard NextAuth session / nsxUser object
            customer_id = data.get("customer_id") or data.get("id") or data.get("userId")
            cpf = data.get("cpf") or data.get("username")
            first_name = data.get("first_name") or data.get("name")
            last_name = data.get("last_name") or ""
            full_name = f"{first_name} {last_name}".strip() if last_name else first_name
            
            raw_balance = data.get("balance", 0.0)
            
            return UserProfile(
                id=int(customer_id) if customer_id else None,
                username=cpf,
                name=full_name,
                cpf=cpf,
                balance=float(raw_balance),
                currency=data.get("currency", "BRL")
            )
        except Exception as e:
            logger.error("Failed to parse user profile: %s. Raw data: %s", e, data)
            raise ValueError(f"User profile parsing error: {e}") from e

    @staticmethod
    def parse_matches(data: List[Dict[str, Any]]) -> List[Match]:
        """Parses a list of raw match items into Match models."""
        matches = []
        for item in data:
            try:
                # Extract markets
                markets_list = []
                for m in item.get("markets", []):
                    outcomes_list = []
                    for o in m.get("outcomes", []):
                        outcomes_list.append(OddOutcome(
                            id=str(o.get("id")),
                            name=o.get("name"),
                            value=float(o.get("value", 0.0))
                        ))
                    markets_list.append(Market(
                        id=str(m.get("id")),
                        name=m.get("name"),
                        outcomes=outcomes_list
                    ))

                matches.append(Match(
                    id=str(item.get("id")),
                    homeTeam=item.get("homeTeam") or item.get("home_team"),
                    awayTeam=item.get("awayTeam") or item.get("away_team"),
                    startTime=item.get("startTime") or item.get("start_time"),
                    sportName=item.get("sportName") or item.get("sport_name"),
                    leagueName=item.get("leagueName") or item.get("league_name"),
                    markets=markets_list
                ))
            except Exception as e:
                logger.warning("Skipping match due to parsing error: %s. Data: %s", e, item)
        return matches

    @staticmethod
    def parse_bet_response(data: Dict[str, Any]) -> PlaceBetResponse:
        """Parses the response of a placed bet."""
        try:
            return PlaceBetResponse(
                success=bool(data.get("success", False)),
                bet_id=str(data.get("betId") or data.get("id", "")),
                message=data.get("message"),
                balance_after=float(data.get("balanceAfter") or data.get("balance", 0.0)) if "balanceAfter" in data or "balance" in data else None
            )
        except Exception as e:
            logger.error("Failed to parse place bet response: %s. Raw data: %s", e, data)
            raise ValueError(f"Bet response parsing error: {e}") from e
