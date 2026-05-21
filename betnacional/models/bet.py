from pydantic import BaseModel, Field
from typing import Optional, List, Any

class BetSelection(BaseModel):
    """Pydantic model representing a selection in a betslip."""
    match_id: str
    market_id: str
    outcome_id: str
    odd_value: float

class PlaceBetRequest(BaseModel):
    """Pydantic model representing a request to place a bet."""
    selection: BetSelection
    stake: float = Field(..., description="Amount of money to wager")

class PlaceBetResponse(BaseModel):
    """Pydantic model representing the response from placing a bet."""
    success: bool
    bet_id: Optional[str] = None
    message: Optional[str] = None
    balance_after: Optional[float] = None

class BetHistoryEvent(BaseModel):
    """Summary of an event within a bet history response."""
    id: Optional[str] = None
    event_id: Optional[int] = None
    home: Optional[str] = None
    home_id: Optional[int] = None
    away: Optional[str] = None
    away_id: Optional[int] = None
    sport_id: Optional[int] = None
    sport_name: Optional[str] = None
    tournament_id: Optional[int] = None
    tournament_name: Optional[str] = None
    event_date: Optional[str] = None
    event_status_id: Optional[Any] = None
    market_status_id: Optional[Any] = None
    cashout_status: Optional[int] = None
    booked: Optional[int] = None
    stream_id: Optional[Any] = None
    match_started: Optional[bool] = None
    probabilities: Optional[Any] = None
    producer_id: Optional[Any] = None

class BetHistoryItem(BaseModel):
    """Individual bet selection within history response."""
    id: Optional[str] = None
    is_owner: Optional[int] = None
    bet_count: Optional[int] = None
    header_id: Optional[int] = None
    bet_status_id: Optional[int] = None
    bet_status_name: Optional[str] = None
    bet_type_id: Optional[int] = None
    bet_type_name: Optional[str] = None
    currency_id: Optional[int] = None
    currency: Optional[str] = None
    commission: Optional[Any] = None
    ticket_id: Optional[str] = None
    header_return: Optional[str] = None
    header_result: Optional[Any] = None
    header_stake: Optional[str] = None
    bet_paid: Optional[Any] = None
    created_at: Optional[str] = None
    bet_paid_at: Optional[str] = None
    sport_id: Optional[int] = None
    sport_name: Optional[str] = None
    event_id: Optional[int] = None
    event_date: Optional[str] = None
    event_status_id: Optional[Any] = None
    bet_event_status_id: Optional[int] = None
    tournament_id: Optional[int] = None
    tournament_name: Optional[str] = None
    market_id: Optional[int] = None
    market_code: Optional[str] = None
    market_name: Optional[str] = None
    market_status_id: Optional[Any] = None
    outcome_id: Optional[str] = None
    outcome_code: Optional[str] = None
    outcome_name: Optional[str] = None
    specifier: Optional[str] = None
    odd: Optional[float] = None
    current_odd: Optional[float] = None
    sr_event_odd_id: Optional[str] = None
    total_odd: Optional[float] = None
    total_odd_return: Optional[Any] = None
    return_type_id: Optional[Any] = None
    home: Optional[str] = None
    home_id: Optional[int] = None
    away: Optional[str] = None
    away_id: Optional[int] = None
    player_name: Optional[Any] = None
    outcome_name_player: Optional[Any] = None
    booked: Optional[int] = None
    stream_id: Optional[Any] = None
    probabilities: Optional[Any] = None
    current_probability: Optional[float] = None
    cashout_status: Optional[int] = None
    producer_id: Optional[Any] = None
    variant: Optional[str] = None
    client_ip: Optional[str] = None
    signature: Optional[str] = None
    signed_at: Optional[str] = None
    signed_at_ts: Optional[int] = None
    is_super_odds: Optional[bool] = None
    is_outright: Optional[bool] = None

class BetHistoryResponse(BaseModel):
    """Response from bet history API endpoint."""
    bets: List[BetHistoryItem] = []
    events: List[BetHistoryEvent] = []
    scores: List[Any] = []
