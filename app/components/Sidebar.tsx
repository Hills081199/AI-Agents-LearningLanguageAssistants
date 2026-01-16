"use client";

import { BookOpen, Clock, FolderOpen, ChevronRight } from 'lucide-react';

interface HistoryItem {
    filename: string;
    topic: string;
    created_at: number;
}

interface SidebarProps {
    history: HistoryItem[];
    onLoadLesson: (filename: string) => void;
    currentLesson?: string;
}

export default function Sidebar({ history, onLoadLesson, currentLesson }: SidebarProps) {
    // Group by date
    const groupedHistory = history.reduce((groups: Record<string, HistoryItem[]>, item) => {
        const date = new Date(item.created_at * 1000).toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
        if (!groups[date]) {
            groups[date] = [];
        }
        groups[date].push(item);
        return groups;
    }, {});

    return (
        <aside className="w-72 bg-gradient-to-b from-slate-900 to-slate-800 text-white flex flex-col h-screen sticky top-0 shadow-2xl">
            {/* Header */}
            <div className="p-6 border-b border-slate-700/50">
                <h1 className="text-xl font-bold flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-teal-400 to-cyan-500 rounded-lg">
                        <BookOpen className="w-5 h-5 text-white" />
                    </div>
                    <span className="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
                        HSK Factory
                    </span>
                </h1>
                <p className="text-slate-400 text-sm mt-2">AI-Powered Chinese Lessons</p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto p-4">
                <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-wider mb-4">
                    <FolderOpen className="w-4 h-4" />
                    <span>Lesson Library</span>
                </div>

                {Object.keys(groupedHistory).length === 0 ? (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-700/50 flex items-center justify-center">
                            <BookOpen className="w-8 h-8 text-slate-500" />
                        </div>
                        <p className="text-slate-500 text-sm">No lessons yet</p>
                        <p className="text-slate-600 text-xs mt-1">Generate your first lesson!</p>
                    </div>
                ) : (
                    Object.entries(groupedHistory).map(([date, items]) => (
                        <div key={date} className="mb-6">
                            <div className="flex items-center gap-2 text-slate-500 text-xs mb-2">
                                <Clock className="w-3 h-3" />
                                <span>{date}</span>
                            </div>
                            <div className="space-y-1">
                                {items.map((item) => {
                                    const isActive = currentLesson === item.filename;
                                    return (
                                        <button
                                            key={item.filename}
                                            onClick={() => onLoadLesson(item.filename)}
                                            className={`
                        w-full text-left p-3 rounded-xl text-sm transition-all duration-200 group
                        flex items-center gap-3
                        ${isActive
                                                    ? 'bg-gradient-to-r from-teal-500/20 to-cyan-500/20 border border-teal-500/30 text-teal-300'
                                                    : 'hover:bg-slate-700/50 text-slate-300 hover:text-white'
                                                }
                      `}
                                        >
                                            <div className={`
                        w-2 h-2 rounded-full transition-all
                        ${isActive ? 'bg-teal-400' : 'bg-slate-600 group-hover:bg-slate-500'}
                      `} />
                                            <span className="flex-1 truncate">{item.topic}</span>
                                            <ChevronRight className={`
                        w-4 h-4 transition-all
                        ${isActive ? 'text-teal-400' : 'text-slate-600 group-hover:text-slate-400'}
                      `} />
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))
                )}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-slate-700/50">
                <div className="text-xs text-slate-500 text-center">
                    Powered by CrewAI 🚀
                </div>
            </div>
        </aside>
    );
}
