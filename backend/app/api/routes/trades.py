from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.models.models import Trade, Account
from app.schemas.schemas import TradeCreate, TradeResponse, TradeValidationRequest, ValidationResult
from app.services.risk_engine import risk_engine
from app.services.delta_service import delta_service
from app.services.report_service import report_service
import io

router = APIRouter()

@router.get("/export/pdf")
def export_trades_pdf(db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    trades = db.query(Trade).filter(Trade.account_id == account.id).order_by(Trade.entry_time.desc()).all()
    
    pdf_bytes = report_service.generate_trade_pdf(trades, account)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=trade_history.pdf"}
    )

@router.post("/validate", response_model=ValidationResult)
def validate_trade_request(
    request: TradeValidationRequest, 
    db: Session = Depends(get_db)
):
    # Assume single user account id=1 for now
    # Calculate params
    entry_price = delta_service.get_mark_price(request.symbol)
    if entry_price <= 0:
         return ValidationResult(valid=False, can_execute=False, reason="Could not determine Entry Price (Market Closed?)")

    # SL Percent to Price
    # Assumes sl_percent is e.g. 1.5 for 1.5%
    if request.side == "LONG":
        stop_loss = entry_price * (1 - (request.sl_percent / 100))
    else:
        stop_loss = entry_price * (1 + (request.sl_percent / 100))

    return risk_engine.validate_trade(db, 1, request.symbol, entry_price, stop_loss, request.quantity)


@router.post("/", response_model=TradeResponse)
def execute_trade(
    trade_in: TradeCreate, 
    db: Session = Depends(get_db)
):
    # 1. Determine Prices
    market_price = delta_service.get_mark_price(trade_in.symbol)
    
    # Logic: If MARKET, force execution price to be market_price (for risk checks).
    # If LIMIT, use limit_price if valid, else fallback to market (for risk checks).
    if trade_in.order_type == "MARKET":
        entry_price = market_price
    else:
        entry_price = trade_in.limit_price if (trade_in.limit_price and trade_in.limit_price > 0) else market_price
    
    if entry_price <= 0:
        raise HTTPException(status_code=400, detail="Unable to fetch price for execution validation")

    if trade_in.side == "LONG":
        stop_loss = entry_price * (1 - (trade_in.sl_percent / 100))
    else:
        stop_loss = entry_price * (1 + (trade_in.sl_percent / 100))
    
    # 2. Re-validate Risk
    validation = risk_engine.validate_trade(db, 1, trade_in.symbol, entry_price, stop_loss, trade_in.quantity)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.reason)
        
    # 2. Execute on Delta Exchange (Sync Block)
    try:
        # Note: Delta expects integer size often for contracts, check spec. 
        # Passing raw qty for now as app handles logic.
        
        # Determine Limit Price based on Order Type
        execution_price = None
        if trade_in.order_type != "MARKET" and trade_in.limit_price and trade_in.limit_price > 0:
            execution_price = trade_in.limit_price

        delta_order = delta_service.place_order(
            symbol=trade_in.symbol,
            side=trade_in.side,
            size=int(trade_in.quantity), # Enforce integer lots
            limit_price=execution_price
        )
        # We can extract actual price/id from delta_order if ready
    except Exception as e:
        # KILL SWITCH: If execution fails, DO NOT record as open trade.
        raise HTTPException(status_code=502, detail=f"Execution Failed: {str(e)}")

    # 3. Save to DB (Only if Delta success)
    account = db.query(Account).first()
    
    trade = Trade(
        account_id=account.id,
        symbol=trade_in.symbol,
        side=trade_in.side,
        quantity=trade_in.quantity,
        entry_price=entry_price, # Recorded entry (Estimated or Limit)
        status="OPEN"
    )
    db.add(trade)
    
    # 4. Update Account Stats
    account.trades_today_count += 1
    
    db.commit()
    db.refresh(trade)
    return trade

@router.get("/", response_model=List[TradeResponse])
def get_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(Trade.entry_time.desc()).offset(skip).limit(limit).all()
    return trades
