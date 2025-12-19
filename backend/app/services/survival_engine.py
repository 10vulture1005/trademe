import math

class SurvivalEngine:
    @staticmethod
    def calculate_runway_days(current_balance: float, max_daily_loss: float) -> float:
        """
        Calculates how many days the account can survive if max daily loss is hit every day
        until balance hits 0 (or a survival threshold).
        """
        if max_daily_loss <= 0:
            return 999.0 # Infinity effectively
        
        # We assume "death" is 0 balance for now, or maybe 50% drawdown.
        # Let's use 0 balance as the hard floor.
        return round(current_balance / max_daily_loss, 1)

    @staticmethod
    def calculate_ruin_probability(win_rate: float, reward_risk_ratio: float, risk_per_trade_percent: float) -> float:
        """
        Approximation of Risk of Ruin.
        Using the simple formula: P(Ruin) = ((1 - W) / (1 + W)) ^ Units
        Note: This is a complex topic, using a simplified heuristic for behavioral feedback.
        """
        # If edge is negative (W * R - (1-W) < 0), ruin is certain (1.0)
        expected_value = (win_rate * reward_risk_ratio) - (1 - win_rate)
        if expected_value <= 0:
            return 1.0
            
        # Simplified formula doesn't apply perfectly to user stats, 
        # but we can use Kelly-like metrics.
        
        # Let's return a "Risk Score" derived from consistency logic for now if specific formula is tricky without trade count.
        # Better approach: required win rate vs actual win rate.
        
        required_win_rate = 1 / (1 + reward_risk_ratio)
        if win_rate < required_win_rate:
            return 1.0 # Will eventually ruin
            
        # If winning, ruin prob is low but non-zero depending on sizing.
        # Returning a heuristic valid for UI display (0.0 to 1.0)
        
        buffer = win_rate - required_win_rate
        # The larger the buffer, the lower the risk.
        # buffer 0.0 -> risk 1.0
        # buffer 0.2 -> risk 0.1
        
        risk = max(0.0, 1.0 - (buffer * 5)) # Linear decay for simplicity
        return round(risk, 2)

survival_engine = SurvivalEngine()
