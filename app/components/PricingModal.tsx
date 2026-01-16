"use client";

import { X, Check, Star, Zap, Crown, Shield } from "lucide-react";
import { useEffect, useState } from "react";

interface PricingModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function PricingModal({ isOpen, onClose }: PricingModalProps) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setVisible(true);
        } else {
            setTimeout(() => setVisible(false), 300); // Wait for animation
        }
    }, [isOpen]);

    if (!visible && !isOpen) return null;

    return (
        <div
            className={`fixed inset-0 z-[100] flex items-center justify-center p-4 transition-all duration-300 ${isOpen ? "opacity-100 visible" : "opacity-0 invisible"
                }`}
        >
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity duration-300"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div
                className={`relative w-full max-w-5xl bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl overflow-hidden border border-white/50 transform transition-all duration-500 ${isOpen ? "scale-100 translate-y-0" : "scale-95 translate-y-10"
                    }`}
            >
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors z-10"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="p-8 md:p-12">
                    <div className="text-center mb-10">
                        <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
                            Unlock Your Full Potential
                        </h2>
                        <p className="text-lg text-slate-500 max-w-2xl mx-auto">
                            Supercharge your Chinese learning journey with our premium plans.
                            Get unlimited AI generations, advanced quizzes, and personalized roadmaps.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                        {/* Free Plan */}
                        <div className="relative group hover:-translate-y-1 transition-transform duration-300">
                            <div className="h-full p-8 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-xl transition-all flex flex-col">
                                <div className="mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-4">
                                        <Star className="w-6 h-6 text-slate-600" />
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900">Starter</h3>
                                    <div className="mt-2 flex items-baseline gap-1">
                                        <span className="text-3xl font-bold text-slate-900">$0</span>
                                        <span className="text-slate-500">/ forever</span>
                                    </div>
                                </div>
                                <div className="space-y-4 mb-8 flex-1">
                                    <Feature text="3 Free AI Lessons per day" />
                                    <Feature text="Basic Vocabulary Lists" />
                                    <Feature text="Standard Quizzes" />
                                    <Feature text="Community Support" />
                                </div>
                                <button className="w-full py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-900 font-semibold rounded-xl transition-colors">
                                    Current Plan
                                </button>
                            </div>
                        </div>

                        {/* Pro Plan */}
                        <div className="relative group transform md:-translate-y-4">
                            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition-opacity" />
                            <div className="relative h-full p-8 bg-slate-900 text-white rounded-2xl shadow-2xl flex flex-col border border-indigo-500/30">
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
                                    Most Popular
                                </div>
                                <div className="mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center mb-4 border border-indigo-500/30">
                                        <Zap className="w-6 h-6 text-indigo-400" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white">Pro Learner</h3>
                                    <div className="mt-2 flex items-baseline gap-1">
                                        <span className="text-3xl font-bold text-white">$9.99</span>
                                        <span className="text-indigo-200">/ month</span>
                                    </div>
                                </div>
                                <div className="space-y-4 mb-8 flex-1">
                                    <Feature text="Unlimited AI Lessons" active />
                                    <Feature text="Advanced Grammar Analysis" active />
                                    <Feature text="Roleplay Chat with AI Tutor" active />
                                    <Feature text="Voice Mode (Speaking Practice)" active />
                                    <Feature text="Priority Support" active />
                                </div>
                                <button className="w-full py-3 px-4 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-400 hover:to-violet-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-indigo-500/25">
                                    Upgrade to Pro
                                </button>
                            </div>
                        </div>

                        {/* Lifetime Plan */}
                        <div className="relative group hover:-translate-y-1 transition-transform duration-300">
                            <div className="h-full p-8 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-xl transition-all flex flex-col">
                                <div className="mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center mb-4">
                                        <Crown className="w-6 h-6 text-amber-600" />
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-900">Lifetime</h3>
                                    <div className="mt-2 flex items-baseline gap-1">
                                        <span className="text-3xl font-bold text-slate-900">$199</span>
                                        <span className="text-slate-500">/ one-time</span>
                                    </div>
                                </div>
                                <div className="space-y-4 mb-8 flex-1">
                                    <Feature text="Everything in Pro" />
                                    <Feature text="Lifetime Updates" />
                                    <Feature text="Offline Mode Download" />
                                    <Feature text="Exclusive Content Packs" />
                                    <Feature text="Early Access to New Features" />
                                </div>
                                <button className="w-full py-3 px-4 bg-white border-2 border-slate-100 hover:border-amber-200 hover:bg-amber-50 text-slate-900 font-semibold rounded-xl transition-all">
                                    Get Lifetime Access
                                </button>
                            </div>
                        </div>

                    </div>

                    <div className="mt-12 text-center">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 rounded-full text-slate-500 text-sm">
                            <Shield className="w-4 h-4" />
                            <span>7-day money-back guarantee. No questions asked.</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Feature({ text, active = false }: { text: string; active?: boolean }) {
    return (
        <div className="flex items-center gap-3">
            <div className={`flex-shrink-0 rounded-full p-0.5 ${active ? "bg-indigo-500/20 text-indigo-300" : "bg-slate-100 text-slate-500"}`}>
                <Check className="w-3 h-3" strokeWidth={3} />
            </div>
            <span className={`text-sm ${active ? "text-slate-300" : "text-slate-600"}`}>{text}</span>
        </div>
    );
}
