from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- Trade Schemas ---
class TradeBase(BaseModel):
    symbol: str
    side: str = Field(..., pattern="^(LONG|SHORT)$")
    quantity: float = Field(..., gt=0)
    
class TradeCreate(TradeBase):
    order_type: str = "LIMIT" # LIMIT | MARKET
    limit_price: Optional[float] = None
    sl_percent: float = Field(..., gt=0)
    tp_percent: float = Field(..., gt=0)

class TradeResponse(TradeBase):
    id: int
    account_id: int
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    r_multiple: Optional[float] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: str
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)

# --- Account Schemas ---
class AccountBase(BaseModel):
    balance: float
    max_daily_loss: float
    max_trades_per_day: int

class AccountResponse(AccountBase):
    id: int
    locked: bool
    current_daily_loss: float
    trades_today_count: int
    last_violation_time: Optional[datetime] = None
    
    # Computed / Extra fields for UI
    runway_days: float = Field(default=0.0) # Calculated by service
    ruin_probability: float = Field(default=0.0) # Calculated by service

    model_config = ConfigDict(from_attributes=True)

# --- Journal Schemas ---
class JournalCreate(BaseModel):
    content: str
    
class JournalResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    sentiment_score: Optional[float] = None
    emotional_tags: List[str] = []
    ai_feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- Risk / Validation Schemas ---
class TradeValidationRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    limit_price: Optional[float] = None
    sl_percent: float
    tp_percent: float

class ValidationResult(BaseModel):
    valid: bool
    reason: Optional[str] = None
    can_execute: bool
    
class RuleViolation(BaseModel):
    rule_name: str
    description: str
    lockout_duration_seconds: int
