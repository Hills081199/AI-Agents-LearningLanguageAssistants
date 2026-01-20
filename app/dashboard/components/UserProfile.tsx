"use client";

import { useAppSelector } from "@/app/lib/hooks";

export default function UserProfile() {
    const { user } = useAppSelector((state) => state.auth);

    if (!user) return null;

    const initials = (user.username || user.email || 'U')[0].toUpperCase();
    const displayName = user.username || user.email?.split('@')[0] || 'Learner';

    return (
        <div className="fixed top-6 right-6 z-50 flex items-center gap-3 p-2 pl-3 pr-2 bg-white/80 backdrop-blur-md border border-slate-200/60 rounded-full shadow-sm hover:shadow-md transition-all cursor-default animate-in fade-in slide-in-from-top-4 duration-700">
            <div className="flex flex-col items-end mr-1">
                <span className="text-xs font-bold text-slate-700 leading-tight">
                    {displayName}
                </span>
                <span className="text-[10px] text-slate-500 leading-tight max-w-[120px] truncate">
                    {user.email}
                </span>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-xs font-bold text-white shadow-md shadow-indigo-500/20">
                {initials}
            </div>
        </div>
    );
}
