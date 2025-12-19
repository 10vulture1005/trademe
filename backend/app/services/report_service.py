from fpdf import FPDF
from app.models.models import Trade, Account
from typing import List
import io

class ReportService:
    def generate_trade_pdf(self, trades: List[Trade], account: Account) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        
        # Title
        pdf.cell(0, 10, f"Trade History Report - Account #{account.id}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)
        
        # Account Summary
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Current Balance: ${account.balance:.2f} | Daily Loss: ${account.current_daily_loss:.2f}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Table Header
        pdf.set_font("helvetica", "B", 10)
        cols = ["ID", "Symbol", "Side", "Size", "Entry", "Exit", "PnL", "Time"]
        # widths roughly: 10, 20, 15, 20, 25, 25, 25, 40 -> Total ~180 (A4 w=210)
        col_widths = [10, 25, 15, 20, 25, 25, 25, 45]
        
        for i, col in enumerate(cols):
            pdf.cell(col_widths[i], 10, col, border=1, align="C")
        pdf.ln()

        # Table Rows
        pdf.set_font("helvetica", "", 9)
        total_pnl = 0
        wins = 0
        for trade in trades:
            pnl = trade.pnl if trade.pnl else 0
            total_pnl += pnl
            if pnl > 0: wins += 1
            
            row_data = [
                str(trade.id),
                trade.symbol,
                trade.side,
                str(trade.quantity),
                f"{trade.entry_price:.2f}",
                f"{trade.exit_price:.2f}" if trade.exit_price else "-",
                f"{pnl:.2f}",
                trade.entry_time.strftime("%Y-%m-%d %H:%M")
            ]
            
            for i, data in enumerate(row_data):
                pdf.cell(col_widths[i], 10, data, border=1, align="C")
            pdf.ln()

        # Footer Summary
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        count = len(trades)
        win_rate = (wins / count * 100) if count > 0 else 0
        
        pdf.cell(0, 10, f"Total Trades: {count} | Win Rate: {win_rate:.1f}% | Total Realized PnL: ${total_pnl:.2f}", new_x="LMARGIN", new_y="NEXT")

        return bytes(pdf.output())

report_service = ReportService()
