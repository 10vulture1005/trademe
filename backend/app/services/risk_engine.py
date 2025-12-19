from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import Account, Trade
from app.schemas.schemas import TradeValidationRequest, ValidationResult, RuleViolation

class RiskEngine:
    @staticmethod
    def validate_trade(db: Session, account_id: int, symbol: str, entry_price: float, stop_loss: float, quantity: float) -> ValidationResult:
        """
        Validates if a trade can be taken based on account rules.
        """
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return ValidationResult(valid=False, can_execute=False, reason="Account not found")
        
        if account.locked:
            return ValidationResult(valid=False, can_execute=False, reason="ACCOUNT LOCKED: Rule Violation")

        # 1. Max Trades Per Day
        if account.trades_today_count >= account.max_trades_per_day:
             return ValidationResult(valid=False, can_execute=False, reason=f"Daily Trade Limit Reached ({account.max_trades_per_day})")

        # 2. Daily Loss Limit
        if account.current_daily_loss >= account.max_daily_loss:
            return ValidationResult(valid=False, can_execute=False, reason="Daily Loss Limit Hit")

        # 0. Check Min SL Distance (Sanity Check)
        sl_pct = abs(entry_price - stop_loss) / entry_price
        if sl_pct < 0.0001: # 0.01% Absolute min sanity
             return ValidationResult(valid=False, can_execute=False, reason=f"SL too tight ({sl_pct*100:.2f}%).")

        # Determine if Inverse or Linear
        # Heuristic: BTCUSD is Inverse (Qty in USD). BTCUSDT is Linear (Qty in Coins).
        is_inverse = symbol.endswith("USD") and not symbol.endswith("USDT")
        
        # 3. Risk Per Trade Check
        if is_inverse:
            # Note: For Inverse, Qty IS the notional value in USD.
            # Risk is roughly: Qty * %Loss
            # SL Percent = (Entry-Stop)/Entry
            base_risk = quantity * sl_pct
            
            # Buffer: Fees on Notional (Qty)
            estimated_buffer = quantity * 0.00075
        else:
            # Linear: Qty is Coins.
            # Risk = |Entry - Stop| * Qty
            base_risk = abs(entry_price - stop_loss) * quantity
            
            # Buffer: Fees on Notional (Entry * Qty)
            notional_value = entry_price * quantity
            estimated_buffer = notional_value * 0.00075 
        
        total_risk_impact = base_risk + estimated_buffer
        
        # Prevent taking risk that would immediately breach daily limit
        current_loss = account.current_daily_loss
        if current_loss + total_risk_impact > account.max_daily_loss:
             return ValidationResult(valid=False, can_execute=False, reason=f"Risk ({total_risk_impact:.2f}) exceeds remaining daily buffer")
        
        return ValidationResult(valid=True, can_execute=True, reason="Trade Approved")

    @staticmethod
    def check_post_trade_rules(db: Session, account: Account, trade: Trade):
        """
        Run after a trade is closed or updated.
        Updates daily stats and checks for lockouts.
        """
        # Update counts
        # This logic assumes we are recalculating or incrementally updating
        # For robustness, we might query all trades today
        pass # To be implemented in the logic flow where trades are closed

risk_engine = RiskEngine()
