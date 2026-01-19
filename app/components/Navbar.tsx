"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Zap, ArrowRight, LayoutDashboard } from "lucide-react";
import { useAppSelector } from "../lib/hooks";

export default function Navbar() {
    const pathname = usePathname();
    const { isAuthenticated } = useAppSelector((state) => state.auth);

    const isActive = (path: string) => pathname === path;

    return (
        <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
            <div className="absolute inset-0 bg-white/70 backdrop-blur-xl border-b border-slate-200/50 shadow-sm" />
            <nav className="relative max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-8">
                    <Link href="/landing" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
                            <Zap className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-lg tracking-tight text-slate-900">Language Factory</span>
                    </Link>

                    <Link
                        href="/about"
                        className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${isActive('/about')
                            ? 'bg-indigo-50 text-indigo-700 shadow-sm ring-1 ring-indigo-200'
                            : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                            }`}
                    >
                        <span>Methodology</span>
                        {isActive('/about') && <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />}
                    </Link>
                </div>

                <div className="flex items-center gap-4">
                    {isAuthenticated ? (
                        <Link
                            href="/dashboard"
                            className="px-4 py-2 bg-indigo-50 text-indigo-600 text-sm font-semibold rounded-lg hover:bg-indigo-100 transition-colors flex items-center gap-2"
                        >
                            <LayoutDashboard className="w-4 h-4" />
                            <span>Dashboard</span>
                        </Link>
                    ) : (
                        <></>
                    )}
                </div>
            </nav>
        </header>
    );
}
