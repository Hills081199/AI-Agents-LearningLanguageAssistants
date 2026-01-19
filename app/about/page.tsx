"use client";

import Link from "next/link";
import {
    Zap,
    Bot,
    Brain,
    Sparkles,
    ArrowLeft,
    PenTool,
    Rocket,
    CheckCircle,
    Construction,
    Globe
} from "lucide-react";
import Navbar from "../components/Navbar";

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50/50 to-pink-50/30 font-sans text-slate-900 overflow-x-hidden">
            {/* Decorative Patterns */}
            <div className="fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light pointer-events-none z-0" />
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none z-0" />

            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-b from-indigo-200/20 to-purple-200/20 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2 animate-float-delayed" />
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-to-t from-pink-200/20 to-indigo-200/20 rounded-full blur-3xl -translate-x-1/2 translate-y-1/2 animate-pulse-slow" />

            <br className="hidden" /> {/* Spacer for strict hydration if needed, but margin works better */}
            <Navbar />

            <main className="max-w-5xl mx-auto px-6 py-12 md:py-20 pt-24 relative z-10">

                {/* Hero */}
                <div className="text-center mb-24 animate-in fade-in slide-in-from-bottom-8 duration-700 relative">
                    {/* Floating Decorative Elements */}
                    {/* <div className="absolute -top-4 -left-12 w-14 h-14 bg-white/80 backdrop-blur-md rounded-2xl shadow-lg flex items-center justify-center rotate-12 animate-float delay-100 hidden lg:flex border border-white/50">
                        <span className="text-2xl">🧠</span>
                    </div>
                    <div className="absolute top-20 -right-8 w-12 h-12 bg-white/80 backdrop-blur-md rounded-xl shadow-lg flex items-center justify-center -rotate-6 animate-float-delayed delay-300 hidden lg:flex border border-white/50">
                        <span className="text-xl">✨</span>
                    </div> */}

                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-indigo-100 rounded-full text-sm font-medium text-indigo-700 shadow-sm mb-8 relative">
                        <Bot className="w-4 h-4" />
                        <span>Behind the Magic</span>
                    </div>
                    <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-slate-900 mb-6">
                        Our AI <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">Methodology</span>
                    </h1>
                    <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
                        How we combine advanced language models to create the perfect personalized learning experience for you.
                    </p>
                </div>

                {/* Methodology Grid */}
                <div className="grid md:grid-cols-2 gap-12 items-center mb-32">
                    <div className="space-y-12">
                        <div className="relative group p-6 bg-white/60 backdrop-blur-sm border border-slate-200 rounded-2xl hover:bg-white hover:shadow-xl transition-all animate-in fade-in slide-in-from-left-8 duration-700">
                            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Brain className="w-6 h-6" />
                            </div>
                            <h3 className="text-xl font-bold mb-3">1. The Curriculum Architect</h3>
                            <p className="text-slate-600 leading-relaxed">
                                Our first agent analyzes your requested topic and level (HSK/CEFR) to structure a lesson plan. It decides which vocabulary words are most relevant and what grammar points fit naturally within the context.
                            </p>
                        </div>

                        <div className="relative group p-6 bg-white/60 backdrop-blur-sm border border-slate-200 rounded-2xl hover:bg-white hover:shadow-xl transition-all animate-in fade-in slide-in-from-left-8 duration-700 delay-100">
                            <div className="w-12 h-12 rounded-xl bg-pink-100 text-pink-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <PenTool className="w-6 h-6" />
                            </div>
                            <h3 className="text-xl font-bold mb-3">2. The Storyteller</h3>
                            <p className="text-slate-600 leading-relaxed">
                                Once the structure is set, the Storyteller agent weaves the selected vocabulary and grammar into an engaging, culturally rich narrative or article. This ensures you learn in context, not in isolation.
                            </p>
                        </div>

                        <div className="relative group p-6 bg-white/60 backdrop-blur-sm border border-slate-200 rounded-2xl hover:bg-white hover:shadow-xl transition-all animate-in fade-in slide-in-from-left-8 duration-700 delay-200">
                            <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Sparkles className="w-6 h-6" />
                            </div>
                            <h3 className="text-xl font-bold mb-3">3. The Quiz Master</h3>
                            <p className="text-slate-600 leading-relaxed">
                                Finally, the Quiz Master generates interactive exercises based specifically on the story you just read. It tests your comprehension, vocabulary retention, and grammar usage with immediate feedback.
                            </p>
                        </div>
                    </div>

                    <div className="relative h-[600px] bg-gradient-to-br from-indigo-600 to-violet-700 rounded-3xl shadow-2xl overflow-hidden flex items-center justify-center p-8 animate-in fade-in slide-in-from-right-8 duration-700">
                        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                        <div className="relative z-10 text-white space-y-8">
                            <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/20">
                                <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center font-bold">U</div>
                                <div>
                                    <div className="text-xs text-indigo-200 uppercase tracking-wide">User Request</div>
                                    <div className="font-medium">"I want to learn about ordering coffee in Beijing at HSK 2 level."</div>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <div className="h-8 w-0.5 bg-gradient-to-b from-white/50 to-transparent"></div>
                            </div>

                            <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/20">
                                <Bot className="w-8 h-8 text-indigo-300" />
                                <div>
                                    <div className="text-xs text-indigo-200 uppercase tracking-wide">AI Processing</div>
                                    <div className="font-medium animate-pulse">Generating vocabulary list... Structuring dialogue... Drafting quiz...</div>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <div className="h-8 w-0.5 bg-gradient-to-b from-white/50 to-transparent"></div>
                            </div>

                            <div className="bg-white text-indigo-900 p-6 rounded-xl shadow-lg">
                                <div className="text-xs text-indigo-500 uppercase tracking-wide mb-2">Final Output</div>
                                <h4 className="font-bold text-lg mb-1">At the Coffee Shop (咖啡店)</h4>
                                <p className="text-sm opacity-80 mb-3">A practical dialogue using HSK 2 vocabulary...</p>
                                <div className="flex gap-2">
                                    <span className="px-2 py-1 bg-indigo-100 rounded text-xs font-bold">Reading</span>
                                    <span className="px-2 py-1 bg-indigo-100 rounded text-xs font-bold">Quiz</span>
                                    <span className="px-2 py-1 bg-indigo-100 rounded text-xs font-bold">Roleplay</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Creator Mode Teaser */}
                <div className="relative rounded-3xl overflow-hidden bg-slate-900 text-white p-12 md:p-16 text-center animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
                    <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
                    <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/30 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
                    <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

                    <div className="relative z-10 max-w-3xl mx-auto">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/50 text-amber-500 rounded-full text-xs font-bold uppercase tracking-wide mb-6">
                            <Construction className="w-3 h-3" />
                            <span>Coming Soon</span>
                        </div>

                        <h2 className="text-3xl md:text-5xl font-bold mb-6">Creator Mode</h2>
                        <p className="text-lg text-slate-300 mb-10 leading-relaxed">
                            Take control of the AI. Soon, you'll be able to design your own lesson templates, define custom vocabulary sets, and share your unique teaching methodology with the community.
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                            <div className="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
                                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center mb-3">
                                    <PenTool className="w-4 h-4 text-indigo-400" />
                                </div>
                                <h4 className="font-bold mb-1">Custom Prompts</h4>
                                <p className="text-xs text-slate-400">Tell the AI exactly how to teach your style.</p>
                            </div>
                            <div className="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
                                <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center mb-3">
                                    <Globe className="w-4 h-4 text-purple-400" /> {/* Note: Globe import missing, switching to Rocket or generic */}
                                    <Rocket className="w-4 h-4 text-purple-400" />
                                </div>
                                <h4 className="font-bold mb-1">Publish & Share</h4>
                                <p className="text-xs text-slate-400">Share your lesson packs with other learners.</p>
                            </div>
                            <div className="p-4 bg-white/5 border border-white/10 rounded-xl backdrop-blur-sm">
                                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center mb-3">
                                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                                </div>
                                <h4 className="font-bold mb-1">Analytics</h4>
                                <p className="text-xs text-slate-400">Track how users engage with your content.</p>
                            </div>
                        </div>

                        <button disabled className="mt-10 px-8 py-3 bg-white/10 border border-white/20 rounded-xl font-medium text-slate-400 cursor-not-allowed hover:bg-white/20 transition-colors flex items-center gap-2 mx-auto">
                            <span>Join Waitlist</span>
                            <span className="text-xs bg-white/20 px-2 py-0.5 rounded">Soon</span>
                        </button>
                    </div>
                </div>

            </main>

            <footer className="border-t border-slate-200/60 bg-white/50 backdrop-blur-sm mt-12">
                <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-2 text-slate-600">
                        <Zap className="w-5 h-5 text-indigo-600" />
                        <span className="font-semibold">Language Factory</span>
                    </div>
                    <p className="text-sm text-slate-500">© 2026 Language Factory. Powered by AI Agents.</p>
                </div>
            </footer>
        </div>
    );
}
