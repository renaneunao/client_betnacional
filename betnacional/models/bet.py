from pydantic import BaseModel, Field
from typing import Optional

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
