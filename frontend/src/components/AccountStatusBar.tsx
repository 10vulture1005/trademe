import { getAccount } from '../api/client';
import { useStore } from '../store/useStore';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Lock, ShieldAlert, TrendingDown } from 'lucide-react';
import clsx from 'clsx';

export const AccountStatusBar = () => {
    const { setAccount } = useStore();
    
    const { data: account, isError } = useQuery({
        queryKey: ['account'],
        queryFn: async () => {
            const data = await getAccount();
            setAccount(data);
            return data;
        }
    });

    if (isError) return <div className="bg-red-900/50 p-2 text-red-200">CONNECTION LOST</div>;
    if (!account) return <div className="text-gray-500">Loading Risk Profile...</div>;

    const runwayColor = account.runway_days < 5 ? 'text-red-500' : account.runway_days < 10 ? 'text-yellow-500' : 'text-green-500';
    
    return (
        <div className={clsx("fixed top-0 left-0 right-0 h-14 bg-trade-surface border-b border-trade-border flex items-center px-6 justify-between z-50", 
            account.locked ? "border-red-600 border-b-4" : ""
        )}>
            {/* Health / Survival */}
            <div className="flex items-center space-x-6">
                <div className="flex flex-col">
                    <span className="text-xs text-gray-400">SURVIVAL RUNWAY</span>
                    <span className={clsx("text-lg font-mono font-bold", runwayColor)}>{account.runway_days.toFixed(1)} DAYS</span>
                </div>
                
                <div className="flex flex-col">
                    <span className="text-xs text-gray-400">PROB. OF RUIN</span>
                    <span className={clsx("text-lg font-mono font-bold", account.ruin_probability > 0.5 ? "text-red-500" : "text-gray-300")}>{(account.ruin_probability * 100).toFixed(0)}%</span>
                </div>
            </div>

             {/* Status Indicators */}
            <div className="flex items-center space-x-4">
                {account.locked && (
                    <div className="flex items-center text-red-500 font-bold animate-pulse">
                        <Lock className="w-5 h-5 mr-2" />
                        ACCOUNT LOCKED
                    </div>
                )}
                {account.current_daily_loss > account.max_daily_loss * 0.8 && !account.locked && (
                    <div className="flex items-center text-yellow-500 font-bold">
                        <AlertTriangle className="w-5 h-5 mr-2" />
                        NEAR LIMIT
                    </div>
                )}
            </div>

            {/* Balance Info */}
            <div className="flex items-center space-x-6 text-right">
                <div className="flex flex-col">
                    <span className="text-xs text-gray-400">DAILY LOSS</span>
                    <span className={clsx("font-mono", account.current_daily_loss > 0 ? "text-red-400" : "text-gray-300")}>
                        -${account.current_daily_loss.toFixed(2)} / ${account.max_daily_loss}
                    </span>
                </div>
                <div className="flex flex-col">
                    <span className="text-xs text-gray-400">BALANCE</span>
                    <span className="text-xl font-mono font-bold text-white">${account.balance.toFixed(2)}</span>
                </div>
            </div>
        </div>
    );
};
