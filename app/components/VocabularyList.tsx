"use client";

import { useState } from 'react';
import { Volume2, VolumeX, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

// TTS language codes mapping
const TTS_CODES: Record<string, string> = {
    chinese: 'zh-CN',
    english: 'en-US',
    spanish: 'es-ES'
};

interface VocabItem {
    // Universal fields
    word?: string;
    meaning: string;
    example?: string;
    example_meaning?: string;
    part_of_speech?: string;
    // Chinese-specific fields
    hanzi?: string;
    pinyin?: string;
    romanization?: string;
    example_pinyin?: string;
    example_romanization?: string;
}

interface VocabularyListProps {
    vocabulary: VocabItem[];
    language?: string;
}

function VocabularyItem({ item, index, language = 'chinese' }: { item: VocabItem, index: number, language?: string }) {
    const [speaking, setSpeaking] = useState(false);
    const [expanded, setExpanded] = useState(false);

    // Get the word to display (handle different field names)
    const displayWord = item.word || item.hanzi || '';
    // Get romanization (pinyin for Chinese, could be IPA for others)
    const displayRomanization = item.romanization || item.pinyin || '';
    // Get example romanization
    const displayExampleRomanization = item.example_romanization || item.example_pinyin || '';
    // Check if this language uses romanization
    const hasRomanization = language === 'chinese' && displayRomanization;

    const speak = (text: string, e: React.MouseEvent) => {
        e.stopPropagation();
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = TTS_CODES[language] || 'en-US';
        utterance.rate = language === 'chinese' ? 0.8 : 0.9;
        setSpeaking(true);
        utterance.onend = () => setSpeaking(false);
        utterance.onerror = () => setSpeaking(false);
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div
            className={`bg-white rounded-xl border transition-all duration-200 ${expanded
                ? 'border-indigo-200 shadow-md ring-1 ring-indigo-50'
                : 'border-slate-200 hover:border-indigo-200 hover:shadow-sm'
                }`}
        >
            <div
                className="p-4 flex items-center gap-4 cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                {/* TTS Button */}
                <button
                    onClick={(e) => speak(displayWord, e)}
                    disabled={speaking}
                    className={`
                        p-2.5 rounded-full transition-all duration-200 shrink-0
                        ${speaking
                            ? 'bg-indigo-100 text-indigo-600 animate-pulse'
                            : 'bg-slate-100 text-slate-500 hover:bg-indigo-100 hover:text-indigo-600'
                        }
                    `}
                    title="Pronounce Word"
                >
                    {speaking ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                </button>

                {/* Content */}
                <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-2 items-center">
                    <div className="flex flex-col">
                        <span className="text-xl font-bold text-slate-800">{displayWord}</span>
                        {hasRomanization && (
                            <span className="text-sm text-indigo-500 font-medium">{displayRomanization}</span>
                        )}
                        {item.part_of_speech && (
                            <span className="text-xs text-slate-400 italic">{item.part_of_speech}</span>
                        )}
                    </div>
                    <div className="text-slate-600 md:col-span-2">
                        {item.meaning}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    {item.example && (
                        <div className={`text-xs px-2 py-1 rounded-md transition-colors ${expanded ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>
                            Ex
                        </div>
                    )}
                    {expanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
            </div>

            {/* Expanded Example */}
            {expanded && item.example && (
                <div className="px-4 pb-4 pt-0 animate-in fade-in slide-in-from-top-1 duration-200">
                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex gap-4">
                        <button
                            onClick={(e) => speak(item.example!, e)}
                            className="mt-1 p-2 h-fit rounded-full bg-white border border-slate-200 text-slate-400 hover:text-indigo-600 hover:border-indigo-200 transition-colors shrink-0"
                            title="Pronounce Sentence"
                        >
                            <Volume2 className="w-4 h-4" />
                        </button>
                        <div className="space-y-1">
                            <div className="font-medium text-slate-800 text-lg">{item.example}</div>
                            {hasRomanization && displayExampleRomanization && (
                                <div className="text-slate-500 text-sm">{displayExampleRomanization}</div>
                            )}
                            {item.example_meaning && (
                                <div className="text-slate-600 text-sm italic border-t border-slate-200/60 pt-1 mt-1">{item.example_meaning}</div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function VocabularyList({ vocabulary, language = 'chinese' }: VocabularyListProps) {
    if (!vocabulary || vocabulary.length === 0) {
        return (
            <div className="text-center py-12 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <p>No vocabulary data available for this lesson.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4 max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                    <span className="p-2 bg-indigo-100 rounded-lg text-indigo-600">
                        <BookOpen className="w-6 h-6" />
                    </span>
                    Core Vocabulary
                </h2>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 text-sm font-medium rounded-full">
                    {vocabulary.length} Words
                </span>
            </div>

            <div className="grid gap-3">
                {vocabulary.map((item, index) => (
                    <VocabularyItem key={index} item={item} index={index} language={language} />
                ))}
            </div>
        </div>
    );
}
