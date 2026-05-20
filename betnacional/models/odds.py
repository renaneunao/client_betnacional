from pydantic import BaseModel, Field
from typing import List, Optional

class OddOutcome(BaseModel):
    """Pydantic model representing an individual betting option/odd."""
    id: str
    name: str = Field(..., description="Name of the outcome (e.g. Home, Draw, Away)")
    value: float = Field(..., description="Odd value (e.g. 1.85)")

class Market(BaseModel):
    """Pydantic model representing a betting market (e.g., Match Result, Over/Under)."""
    id: str
    name: str
    outcomes: List[OddOutcome] = []

class Match(BaseModel):
    """Pydantic model representing a sports fixture (match)."""
    id: str
    home_team: str = Field(..., alias="homeTeam")
    away_team: str = Field(..., alias="awayTeam")
    start_time: str = Field(..., alias="startTime")
    sport_name: str = Field(..., alias="sportName")
    league_name: str = Field(..., alias="leagueName")
    markets: List[Market] = []
    
    class Config:
        populate_by_name = True
