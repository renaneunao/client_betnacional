from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    """Pydantic model for authentication request payload."""
    cpf: str = Field(..., description="User CPF (username)")
    password: str = Field(..., description="User password")

class UserProfile(BaseModel):
    """Pydantic model for authenticated user profile data."""
    id: Optional[int] = None
    username: Optional[str] = None
    name: Optional[str] = None
    cpf: Optional[str] = None
    balance: float = Field(0.0, description="Available account balance")
    currency: str = Field("BRL", description="Account currency")
