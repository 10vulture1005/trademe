import { create } from 'zustand';
import { Account } from '../types';

interface AppState {
    account: Account | null;
    isSurvivalMode: boolean; // Derived or explicitly set
    setAccount: (account: Account) => void;
    updateBalance: (newBalance: number) => void;
}

export const useStore = create<AppState>((set) => ({
    account: null,
    isSurvivalMode: false,
    setAccount: (account) => set({ 
        account,
        isSurvivalMode: account.runway_days < 5.0 
    }),
    updateBalance: (bal) => set((state) => ({
        account: state.account ? { ...state.account, balance: bal } : null
    })),
}));
