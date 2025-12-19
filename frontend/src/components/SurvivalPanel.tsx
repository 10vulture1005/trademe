import { Shield, Skull, Download } from 'lucide-react';
import { useStore } from '../store/useStore';
import { exportTradesPdf } from '../api/client';

export const SurvivalPanel = () => {
    const { account, isSurvivalMode } = useStore();

    if (!account) return null;

    const handleDownload = async () => {
        try {
            const blob = await exportTradesPdf();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `trade_report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (e) {
            console.error("Download failed", e);
            alert("Failed to download report");
        }
    };

    return (
        <div className="bg-trade-surface border border-trade-border p-4 rounded-lg mb-4">
            <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-2">Survival Analysis</h3>
            
            {isSurvivalMode ? (
                <div className="bg-red-900/20 border border-red-500/50 p-3 rounded flex items-start space-x-3 mb-3">
                    <Skull className="w-6 h-6 text-red-500 shrink-0" />
                    <div>
                        <p className="text-red-400 font-bold text-sm">CRITICAL SURVIVAL MODE ACTIVE</p>
                        <p className="text-red-300 text-xs mt-1">
                            Runway is under 5 days. Position sizes are HALVED. 
                            Focus on capital preservation. Do not chase losses.
                        </p>
                    </div>
                </div>
            ) : (
                <div className="bg-green-900/10 border border-green-500/20 p-3 rounded flex items-start space-x-3 mb-3">
                    <Shield className="w-5 h-5 text-green-500 shrink-0" />
                    <div>
                        <p className="text-green-400 font-bold text-sm">Systems Nominal</p>
                        <p className="text-gray-400 text-xs mt-1">
                            Maintain logic. Adhere to limits. 
                            You are {account.trades_today_count} / {account.max_trades_per_day} trades today.
                        </p>
                    </div>
                </div>
            )}

            <button 
                onClick={handleDownload}
                className="w-full flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs py-2 rounded transition-colors border border-gray-700"
            >
                <Download className="w-4 h-4" />
                <span>DOWNLOAD TRADE REPORT</span>
            </button>
        </div>
    );
};
