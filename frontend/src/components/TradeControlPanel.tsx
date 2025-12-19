import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { validateTrade, executeTrade } from '../api/client';
import { useStore } from '../store/useStore';
import { clsx } from 'clsx';
import { AlertTriangle, CheckCircle, Ban } from 'lucide-react';

export const TradeControlPanel = () => {
    const { account } = useStore();
    const queryClient = useQueryClient();
    
    // State
    const [symbol, setSymbol] = useState('BTCUSD');
    const [side, setSide] = useState<'LONG' | 'SHORT'>('LONG');
    const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
    const [qty, setQty] = useState(1);
    const [limitPrice, setLimitPrice] = useState(0); 
    const [slPercent, setSlPercent] = useState(0.2);
    const [tpPercent, setTpPercent] = useState(1.0);
    
    // Validation State
    const [validationError, setValidationError] = useState<string | null>(null);
    const [isValidated, setIsValidated] = useState(false);

    const validateMutation = useMutation({
        mutationFn: validateTrade,
        onSuccess: (data) => {
            if (data.valid) {
                setIsValidated(true);
                setValidationError(null);
            } else {
                setIsValidated(false);
                setValidationError(data.reason);
            }
        },
        onError: () => {
            setValidationError("Validation Service Unavailable");
            setIsValidated(false);
        }
    });

    const executeMutation = useMutation({
        mutationFn: async () => executeTrade({ 
            symbol, side, quantity: qty, sl_percent: slPercent, tp_percent: tpPercent, order_type: orderType, limit_price: limitPrice 
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['account'] });
            queryClient.invalidateQueries({ queryKey: ['trades'] });
            setIsValidated(false); // Reset
            // Reset form optionally
        }
    });

    const handleValidate = () => {
        validateMutation.mutate({
            symbol, side, quantity: qty, sl_percent: slPercent, tp_percent: tpPercent, order_type: orderType, limit_price: limitPrice
        });
    };

    const handleExecute = () => {
        if (!isValidated) return;
        executeMutation.mutate();
    };

    const isLocked = account?.locked;

    return (
        <div className="bg-trade-surface border border-trade-border p-4 rounded-lg">
            <div className="flex justify-between items-center mb-4 border-b border-trade-border pb-2">
                 <h3 className="text-gray-400 text-xs font-bold uppercase tracking-wider">Execution Protocol</h3>
                 <div className="flex space-x-2">
                    <button onClick={() => setOrderType('MARKET')} 
                        className={clsx("text-[10px] font-bold px-2 py-1 rounded transition-colors", orderType === 'MARKET' ? "bg-trade-primary text-white" : "text-gray-500 hover:text-white")}
                    >
                        MKT
                    </button>
                    <button onClick={() => setOrderType('LIMIT')} 
                        className={clsx("text-[10px] font-bold px-2 py-1 rounded transition-colors", orderType === 'LIMIT' ? "bg-trade-primary text-white" : "text-gray-500 hover:text-white")}
                    >
                        LMT
                    </button>
                 </div>
            </div>
            
            {isLocked && (
                <div className="absolute inset-0 bg-black/80 z-10 flex items-center justify-center rounded-lg">
                    <div className="text-center">
                        <Ban className="w-12 h-12 text-red-600 mx-auto mb-2" />
                        <h2 className="text-red-500 font-bold text-xl">EXECUTION LOCKED</h2>
                        <p className="text-gray-400 text-xs">Behavioral Kill-Switch Active</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="col-span-2">
                    <label className="text-xs text-gray-500">SYMBOL</label>
                    <input type="text" value={symbol} onChange={e => setSymbol(e.target.value)} 
                        className="w-full bg-black border border-trade-border p-2 text-white font-mono uppercase focus:border-trade-primary outline-none" 
                    />
                </div>
                
                <button onClick={() => setSide('LONG')} className={clsx("p-2 font-bold text-xs border transition-colors", side === 'LONG' ? "bg-green-900/50 border-green-500 text-green-400" : "border-trade-border text-gray-500")}>
                    LONG
                </button>
                <button onClick={() => setSide('SHORT')} className={clsx("p-2 font-bold text-xs border transition-colors", side === 'SHORT' ? "bg-red-900/50 border-red-500 text-red-400" : "border-trade-border text-gray-500")}>
                    SHORT
                </button>

                <div>
                    <label className="text-xs text-gray-500">SIZE (Lots as Integer)</label>
                    <input type="number" step="1" min="1" value={qty} onChange={e => setQty(parseInt(e.target.value) || 0)} 
                        className="w-full bg-black border border-trade-border p-2 text-white font-mono focus:border-trade-primary outline-none" 
                    />
                </div>
                 
                {orderType === 'LIMIT' && (
                    <div>
                        <label className="text-xs text-gray-500">LIMIT PRICE ($)</label>
                        <input type="number" value={limitPrice} onChange={e => setLimitPrice(parseFloat(e.target.value))} 
                            className="w-full bg-black border border-trade-border p-2 text-white font-mono focus:border-trade-primary outline-none" 
                        />
                    </div>
                )}

                <div>
                    <label className="text-xs text-gray-500">SL %</label>
                    <input type="number" step="0.01" min="0.01" value={slPercent} onChange={e => setSlPercent(parseFloat(e.target.value))} 
                        className="w-full bg-black border border-red-900/50 p-2 text-red-400 font-mono focus:border-red-500 outline-none" 
                    />
                </div>
                <div>
                    <label className="text-xs text-gray-500">TP %</label>
                    <input type="number" step="0.1" value={tpPercent} onChange={e => setTpPercent(parseFloat(e.target.value))} 
                        className="w-full bg-black border border-green-900/50 p-2 text-green-400 font-mono focus:border-green-500 outline-none" 
                    />
                </div>
            </div>

            {/* Validation Feedback */}
            {validationError && (
                <div className="mb-4 bg-red-900/20 border border-red-500/50 p-2 text-red-400 text-xs flex items-center">
                    <Ban className="w-4 h-4 mr-2" />
                    {validationError}
                </div>
            )}

            {/* Actions */}
            <div className="flex space-x-2">
                {!isValidated ? (
                    <button onClick={handleValidate} disabled={validateMutation.isPending}
                        className="flex-1 bg-trade-surface border border-trade-primary text-trade-primary py-3 font-bold text-sm hover:bg-trade-primary/10 transition-colors uppercase"
                    >
                        {validateMutation.isPending ? 'Checking Risk...' : 'Validate Trade'}
                    </button>
                ) : (
                    <button onClick={handleExecute} disabled={executeMutation.isPending}
                        className="flex-1 bg-trade-primary text-white py-3 font-bold text-sm hover:bg-blue-600 transition-colors shadow-[0_0_15px_rgba(37,99,235,0.5)] flex items-center justify-center"
                    >
                        {executeMutation.isPending ? 'Executing...' : (
                            <>
                                <CheckCircle className="w-4 h-4 mr-2" />
                                {orderType === 'MARKET' ? 'MARKET BUY' : 'PLACE LIMIT'}
                            </>
                        )}
                    </button>
                )}
            </div>
             {isValidated && <p className="text-center text-xs text-green-500 mt-2">RISK APPROVED. READY.</p>}
        </div>
    );
};
