import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { createJournalEntry, getJournalEntries } from '../api/client';
import { Send, Bot, User, BrainCircuit } from 'lucide-react';
import { clsx } from 'clsx';
import { JournalEntry } from '../types';

export const AiChatBot = () => {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [input, setInput] = useState('');
    
    // Fetch History
    const { data: history, isLoading } = useQuery({
        queryKey: ['journal'],
        queryFn: getJournalEntries,
        refetchInterval: 10000 
    });

    const mutation = useMutation({
        mutationFn: createJournalEntry,
        onSuccess: () => {
             setInput('');
             // React Query normally handles refetch, but we want immediate UI update
             // We can optimistically update or just wait for refetch.
             // For chat feel, waiting is okay if fast.
        }
    });

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history, mutation.isPending]);

    const handleSend = () => {
        if (!input.trim()) return;
        mutation.mutate(input);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Sort history by time ascending for chat
    const sortedHistory = history ? [...history].reverse() : [];

    return (
        <div className="bg-trade-surface border border-trade-border rounded-lg flex flex-col h-full min-h-[400px]">
            <div className="p-3 border-b border-trade-border flex items-center space-x-2 bg-black/20">
                <BrainCircuit className="w-5 h-5 text-trade-primary" />
                <h3 className="text-gray-300 text-sm font-bold uppercase tracking-wider">AI Performance Coach</h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {isLoading && <div className="text-center text-gray-600 text-xs">Loading context...</div>}
                
                {/* Intro Message */}
                <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-full bg-trade-primary/20 flex items-center justify-center border border-trade-primary/30 shrink-0">
                        <Bot className="w-4 h-4 text-trade-primary" />
                    </div>
                    <div className="bg-black/40 border border-trade-border rounded-r-lg rounded-bl-lg p-3 max-w-[85%]">
                         <p className="text-gray-300 text-sm leading-relaxed">
                            I am your AI Analyst. I'm here to support your trading. 
                            Tell me how you're feeling or explain your trade plan. 
                            I'll check your risk and psychology.
                         </p>
                    </div>
                </div>

                {sortedHistory.map((entry: JournalEntry) => (
                    <div key={entry.id}>
                        {/* User Message */}
                        <div className="flex items-start justify-end space-x-3 mb-4">
                             <div className="bg-trade-primary/10 border border-trade-primary/30 rounded-l-lg rounded-br-lg p-3 max-w-[85%]">
                                <p className="text-gray-200 text-sm">{entry.content}</p>
                            </div>
                            <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center border border-white/10 shrink-0">
                                <User className="w-4 h-4 text-gray-400" />
                            </div>
                        </div>

                        {/* AI Response */}
                        <div className="flex items-start space-x-3">
                            <div className="w-8 h-8 rounded-full bg-trade-primary/20 flex items-center justify-center border border-trade-primary/30 shrink-0">
                                <Bot className="w-4 h-4 text-trade-primary" />
                            </div>
                            <div className="bg-black/40 border border-trade-border rounded-r-lg rounded-bl-lg p-3 max-w-[85%]">
                                <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
                                    {entry.ai_feedback || "Analyzing..."}
                                </p>
                                {entry.emotional_tags && entry.emotional_tags.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2">
                                        {entry.emotional_tags.map(tag => (
                                            <span key={tag} className="text-[10px] bg-white/5 text-gray-400 px-2 py-0.5 rounded-full border border-white/5 uppercase">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {mutation.isPending && (
                     <div className="flex items-start justify-end space-x-3 mb-4 opacity-50">
                        <div className="bg-trade-primary/10 border border-trade-primary/30 rounded-l-lg rounded-br-lg p-3 max-w-[85%]">
                           <p className="text-gray-200 text-sm">{input}</p>
                       </div>
                    </div>
                )}
                 {mutation.isPending && (
                    <div className="flex items-start space-x-3 animate-pulse">
                         <div className="w-8 h-8 rounded-full bg-trade-primary/20 flex items-center justify-center border border-trade-primary/30 shrink-0">
                            <Bot className="w-4 h-4 text-trade-primary" />
                        </div>
                        <div className="flex space-x-1 items-center h-8">
                             <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                             <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                             <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                        </div>
                    </div>
                 )}
            </div>

            <div className="p-3 border-t border-trade-border bg-black/20">
                <div className="relative">
                    <textarea 
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a message..."
                        className="w-full bg-black border border-trade-border rounded-lg pl-3 pr-10 py-3 text-sm text-gray-300 focus:border-trade-primary outline-none resize-none h-12 min-h-[48px]"
                    />
                    <button 
                        onClick={handleSend}
                        disabled={mutation.isPending || !input.trim()}
                        className={clsx("absolute right-2 top-2 p-1.5 rounded-md transition-all", 
                            input.trim() ? "bg-trade-primary text-white hover:bg-blue-600" : "text-gray-600 cursor-not-allowed"
                        )}
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
};
