export interface Account {
    id: number;
    balance: number;
    locked: boolean;
    max_daily_loss: number;
    current_daily_loss: number;
    max_trades_per_day: number;
    trades_today_count: number;
    last_violation_time: string | null;
    runway_days: number;
    ruin_probability: number;
}

export interface Trade {
    id: number;
    symbol: string;
    side: 'LONG' | 'SHORT';
    quantity: number;
    entry_price: number;
    exit_price: number | null;
    pnl: number | null;
    r_multiple: number | null;
    entry_time: string;
    exit_time: string | null;
    status: string;
    tags: string[];
}

export interface TradeCreate {
    symbol: string;
    side: 'LONG' | 'SHORT';
    quantity: number;
    limit_price?: number;
    sl_percent: number;
    tp_percent: number;
    order_type?: 'LIMIT' | 'MARKET';
}

export interface TradeValidationRequest extends TradeCreate {}

export interface ValidationResult {
    valid: boolean;
    reason: string | null;
    can_execute: boolean;
}

export interface JournalEntry {
    id: number;
    content: string;
    created_at: string;
    sentiment_score: number | null;
    emotional_tags: string[];
    ai_feedback: string | null;
}
