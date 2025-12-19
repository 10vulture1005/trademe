from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    balance: Mapped[float] = mapped_column(Float, default=10000.0)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Risk Settings (Per account overrides)
    max_daily_loss: Mapped[float] = mapped_column(Float, default=300.0) # Absolute $ amount or R calc
    max_trades_per_day: Mapped[int] = mapped_column(Integer, default=5)
    
    # Current Day State (Reset daily via cron or checked on request)
    current_daily_loss: Mapped[float] = mapped_column(Float, default=0.0)
    trades_today_count: Mapped[int] = mapped_column(Integer, default=0)
    last_violation_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    trades: Mapped[List["Trade"]] = relationship("Trade", back_populates="account")
    journal_entries: Mapped[List["JournalEntry"]] = relationship("JournalEntry", back_populates="account")

class Trade(Base):
    __tablename__ = "trades"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"))
    
    symbol: Mapped[str] = mapped_column(String, index=True)
    side: Mapped[str] = mapped_column(String) # LONG / SHORT
    quantity: Mapped[float] = mapped_column(Float)
    
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    r_multiple: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="OPEN") # OPEN, CLOSED, REJECTED
    
    # AI Tags
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list) # ["revenge", "fomo"]
    
    account: Mapped["Account"] = relationship("Account", back_populates="trades")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"))
    
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # AI Analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    emotional_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    account: Mapped["Account"] = relationship("Account", back_populates="journal_entries")
