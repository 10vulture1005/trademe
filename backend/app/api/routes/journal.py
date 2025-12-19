from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.models import JournalEntry, Account
from app.schemas.schemas import JournalCreate, JournalResponse
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.post("/", response_model=JournalResponse)
async def create_journal_entry(entry_in: JournalCreate, db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 1. AI Analysis
    account_stats = {
        "balance": account.balance,
        "current_daily_loss": account.current_daily_loss,
        "max_daily_loss": account.max_daily_loss,
        "trades_today_count": account.trades_today_count
    }
    analysis = await gemini_service.analyze_journal(entry_in.content, account_stats)
    
    # 2. Save
    entry = JournalEntry(
        account_id=account.id,
        content=entry_in.content,
        sentiment_score=analysis.get("sentiment_score"),
        emotional_tags=analysis.get("emotional_tags"),
        ai_feedback=analysis.get("ai_feedback")
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return entry

@router.get("/", response_model=List[JournalResponse])
def get_journal_entries(db: Session = Depends(get_db)):
    entries = db.query(JournalEntry).order_by(JournalEntry.created_at.desc()).limit(50).all()
    return entries
