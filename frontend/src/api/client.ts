import axios from 'axios';
import { Account, Trade, TradeCreate, TradeValidationRequest, ValidationResult, JournalEntry } from '../types';

const API_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getAccount = async (): Promise<Account> => {
    const response = await api.get<Account>('/account/');
    return response.data;
};

export const validateTrade = async (data: TradeValidationRequest): Promise<ValidationResult> => {
    const response = await api.post<ValidationResult>('/trades/validate', data);
    return response.data;
};

export const executeTrade = async (data: TradeCreate): Promise<Trade> => {
    const response = await api.post<Trade>('/trades/', data);
    return response.data;
};

export const getTrades = async (): Promise<Trade[]> => {
    const response = await api.get<Trade[]>('/trades/');
    return response.data;
};

export const createJournalEntry = async (content: string): Promise<JournalEntry> => {
    const response = await api.post<JournalEntry>('/journal/', { content });
    return response.data;
};

export const getJournalEntries = async (): Promise<JournalEntry[]> => {
    const response = await api.get<JournalEntry[]>('/journal/');
    return response.data;
};

export const exportTradesPdf = async (): Promise<Blob> => {
    const response = await api.get('/trades/export/pdf', {
        responseType: 'blob',
    });
    return response.data;
};
