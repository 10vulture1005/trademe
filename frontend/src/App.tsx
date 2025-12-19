import { AccountStatusBar } from './components/AccountStatusBar';
import { SurvivalPanel } from './components/SurvivalPanel';
import { TradeControlPanel } from './components/TradeControlPanel';
import { Activity } from 'lucide-react';
import TradingViewWidget from './components/TradingViewWidget';

function App() {
  return (
    <div className="min-h-screen bg-trade-bg text-gray-300 font-sans pt-14 flex flex-col">
      <AccountStatusBar />
      
      <main className="flex-1 p-6 grid grid-cols-12 gap-6">
        {/* Left Column: Charts & Analysis (TradingView placeholder) */}
        <div className="col-span-8 flex flex-col space-y-4">
            {/* TradingView Widget */}
            <div className="flex-1 bg-trade-surface border border-trade-border rounded-lg overflow-hidden min-h-[500px]">
                <TradingViewWidget />
            </div>
            {/* Recent Trades / Journal could go here */}
        </div>

        {/* Right Column: Control & Survival */}
        <div className="col-span-4 flex flex-col space-y-6">
            <SurvivalPanel />
            <TradeControlPanel />
            
            {/* Rules / Journal Prompt */}
            <div className="flex-1 min-h-[400px] bg-trade-surface border border-trade-border rounded-lg p-4 flex flex-col justify-center items-center text-gray-500">
                 <p>AI Bot Removed.</p>
                 {/* Placeholder for future widgets or emptiness */}
            </div>
        </div>
      </main>
    </div>
  )
}

export default App
