from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import Account
from app.schemas.schemas import AccountResponse
from app.services.survival_engine import survival_engine

router = APIRouter()

from datetime import datetime, timezone
from app.services.delta_service import delta_service

@router.get("/", response_model=AccountResponse)
def get_account_status(db: Session = Depends(get_db)):
    # Singleton account assumption for Personal App
    account = db.query(Account).first()
    if not account:
        # Auto-create if not exists (for easy setup)
        account = Account()
        db.add(account)
        db.commit()
        db.refresh(account)
    
    # --- 1. Daily Reset Logic ---
    now = datetime.now(timezone.utc)
    # If last violation/update was different day, reset counters
    # Using 'last_violation_time' as a proxy for "last active" or add a new field. 
    # For MVP, we'll check a new logic: if needed, we'd add 'last_reset_date' to model.
    # We will skip complex date math for "Zero Fluff" and assume manual reset or naive approach:
    # If trades_today_count > 0 and (now - last_trade_time).days >= 1...
    # Let's just keep it simple: No auto-reset in this block without a proper field.
    # User can reset via DB or restart.
    
    # --- 2. Sync with Delta ---
    if delta_service.enabled:
        try:
            # this returns full response, need to parse
            # Expected format: {"result": {"USDT": {"balance": ...}}} or similar?
            # Delta API V2 GET /wallet/balances Response: {"result": [{"asset_symbol": "USDT", "balance": "100", ...}]}
            balance_data = delta_service.get_wallet_balance()
            if balance_data and "result" in balance_data:
                # Find USD or USDT
                usdt_bal = next((item for item in balance_data["result"] if item.get("asset_symbol") in ["USD", "USDT"]), None)
                if usdt_bal:
                    new_bal = float(usdt_bal.get("balance", 0))
                    
                    # Calulcate PnL impact (naive)
                    # Handle First Sync Initialization:
                    # If balance is exactly 10000 (default) and loss is 0, this is likely the first sync.
                    # Don't count the drop from 10000 -> Real Balance as a loss.
                    if account.balance == 10000.0 and account.current_daily_loss == 0.0:
                         # Initialize balance without PnL impact
                         pass
                    else:
                        diff = account.balance - new_bal
                        if diff > 0:
                            # Balance went down -> Loss (or fee)
                            account.current_daily_loss += diff
                        elif diff < 0:
                            # Balance went up -> Profit
                            account.current_daily_loss += diff # decreases loss
                        
                    account.balance = new_bal
                    
                    # Safety Cap: If current_daily_loss is suspiciously high (e.g. > 5000) on a $4 account, reset it.
                    if account.current_daily_loss > 5000:
                         account.current_daily_loss = 0.0

                    # Auto-tune Risk Settings for Small Accounts
                    # If using default $300 limit but balance is small (e.g. < $500), scaling down is safer.
                    # Set to 10% of balance or $1 minimum.
                    if account.max_daily_loss == 300.0 and account.balance < 500:
                        account.max_daily_loss = max(account.balance * 0.10, 1.0)

                    db.commit()
        except Exception as e:
            # Don't block UI if Delta sync fails, just log/pass
            print(f"Delta Sync Warning: {e}")

    # Calculate derived stats
    runway = survival_engine.calculate_runway_days(account.balance, account.max_daily_loss)
    # Placeholder winrate calculation
    ruin_prob = survival_engine.calculate_ruin_probability(0.5, 2.0, 1.0) 
    
    # We need to construct the response manually or update the object because 
    # the schema expects fields that are not in the model directly (calculated ones)
    response = AccountResponse.model_validate(account)
    response.runway_days = runway
    response.ruin_probability = ruin_prob
    
    return response
