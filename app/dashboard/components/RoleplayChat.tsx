"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, MessageCircle, X } from 'lucide-react';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

interface RoleplayChatProps {
    lessonContext: string;
    characterName?: string;
    language?: string;
}

// Language-specific configurations
const LANGUAGE_CONFIG: Record<string, { greeting: string; prompt: string; placeholder: string; subtitle: string }> = {
    chinese: {
        greeting: '你好！我是你的中文老师。有什么问题吗？(Hello! I am your Chinese teacher. Do you have any questions?)',
        prompt: 'Try: "你好" or "这课讲什么?"',
        placeholder: 'Type in Chinese or English...',
        subtitle: 'Practice your Chinese'
    },
    english: {
        greeting: 'Hello! I am your English teacher. Feel free to ask me anything about the lesson!',
        prompt: 'Try: "Can you explain this word?" or "What does this phrase mean?"',
        placeholder: 'Type your message...',
        subtitle: 'Practice your English'
    },
    spanish: {
        greeting: '¡Hola! Soy tu profesor de español. ¿Tienes alguna pregunta? (Hello! I am your Spanish teacher. Do you have any questions?)',
        prompt: 'Try: "¿Qué significa...?" or "¿Cómo se usa...?"',
        placeholder: 'Escribe en español o inglés...',
        subtitle: 'Practice your Spanish'
    }
};

export default function RoleplayChat({ lessonContext, characterName, language = "chinese" }: RoleplayChatProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Get language-specific config
    const langConfig = LANGUAGE_CONFIG[language] || LANGUAGE_CONFIG.english;

    // Default character name based on language
    const defaultNames: Record<string, string> = {
        chinese: 'Teacher Li',
        english: 'Teacher Sarah',
        spanish: 'Profesor García'
    };
    const displayName = characterName || defaultNames[language] || 'Teacher';

    // Determine API base URL dynamically
    const [apiBaseUrl, setApiBaseUrl] = useState("http://127.0.0.1:8000");

    useEffect(() => {
        if (typeof window !== "undefined") {
            const host = window.location.hostname;
            if (host !== "localhost" && host !== "127.0.0.1") {
                setApiBaseUrl(`http://${host}:8000`);
            }
        }
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setLoading(true);

        try {
            const response = await fetch(`${apiBaseUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    context: lessonContext,
                    history: messages,
                    language: language,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: 'Sorry, I cannot respond right now. Please try again later.'
                }]);
            }
        } catch (error) {
            // If chat endpoint doesn't exist yet, provide a mock response
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: langConfig.greeting
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-purple-500 to-indigo-500 
                     rounded-full shadow-lg flex items-center justify-center text-white
                     hover:scale-110 transition-transform duration-200 z-50"
                    title="Chat with your teacher"
                >
                    <MessageCircle className="w-6 h-6" />
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl 
                        flex flex-col overflow-hidden z-50 border border-slate-200">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                                <Bot className="w-6 h-6" />
                            </div>
                            <div>
                                <div className="font-semibold">{displayName}</div>
                                <div className="text-xs text-white/80">{langConfig.subtitle}</div>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-2 hover:bg-white/20 rounded-full transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                        {messages.length === 0 && (
                            <div className="text-center text-slate-400 py-8">
                                <Bot className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                                <p className="text-sm">Start a conversation!</p>
                                <p className="text-xs mt-1">{langConfig.prompt}</p>
                            </div>
                        )}

                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 
                                  flex items-center justify-center flex-shrink-0">
                                        <Bot className="w-4 h-4 text-white" />
                                    </div>
                                )}
                                <div
                                    className={`max-w-[75%] p-3 rounded-2xl ${msg.role === 'user'
                                        ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white rounded-br-md'
                                        : 'bg-white text-slate-800 shadow-sm border border-slate-100 rounded-bl-md'
                                        }`}
                                >
                                    {msg.content}
                                </div>
                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                                        <User className="w-4 h-4 text-slate-600" />
                                    </div>
                                )}
                            </div>
                        ))}

                        {loading && (
                            <div className="flex gap-2 justify-start">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 
                                flex items-center justify-center">
                                    <Bot className="w-4 h-4 text-white" />
                                </div>
                                <div className="bg-white p-3 rounded-2xl rounded-bl-md shadow-sm border border-slate-100">
                                    <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-slate-200 bg-white">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                                placeholder={langConfig.placeholder}
                                className="flex-1 p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                            />
                            <button
                                onClick={sendMessage}
                                disabled={loading || !input.trim()}
                                className="p-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-xl
                           hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
