"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, Shuffle, Volume2 } from 'lucide-react';

// TTS language codes mapping
const TTS_CODES: Record<string, string> = {
    chinese: 'zh-CN',
    english: 'en-US',
    spanish: 'es-ES'
};

interface MatchingPair {
    word?: string;
    hanzi?: string;
    meaning: string;
}

interface MatchingExercise {
    type: 'matching';
    pairs: MatchingPair[];
}

interface MatchingQuizProps {
    exercises: MatchingExercise[];
    language?: string;
    matches: Record<string, string>; // word -> meaning
    onMatch: (word: string, meaning: string) => void;
    isSubmitted: boolean;
    onReset?: () => void;
}

export default function MatchingQuiz({ exercises, language = 'chinese', matches, onMatch, isSubmitted, onReset }: MatchingQuizProps) {
    // Local UI state
    const [selectedWord, setSelectedWord] = useState<string | null>(null);
    const [shuffledMeanings, setShuffledMeanings] = useState<string[]>([]);

    // Combine all pairs
    const allPairs = exercises.flatMap(e => e.pairs);
    const getWord = (pair: MatchingPair) => pair.word || pair.hanzi || '';

    // Initialize shuffled meanings
    useEffect(() => {
        setShuffledMeanings(allPairs.map(p => p.meaning).sort(() => Math.random() - 0.5));
    }, [exercises]);

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = TTS_CODES[language] || 'en-US';
        utterance.rate = language === 'chinese' ? 0.8 : 0.9;
        speechSynthesis.speak(utterance);
    };

    const handleWordClick = (word: string) => {
        if (isSubmitted) return;
        if (matches[word]) return;
        setSelectedWord(word);
    };

    const handleMeaningClick = (meaning: string) => {
        if (isSubmitted) return;
        if (!selectedWord) return;
        if (Object.values(matches).includes(meaning)) return;

        // In controlled mode, we trust the user logic? Or we validate here?
        // Parent expects onMatch(word, meaning).
        // Validation happens in Parent? Or we allow any match?
        // Original logic: ONLY allowed correct match. "if (correctPair...)"
        // User wants "Submit to check".
        // SO WE MUST ALLOW WRONG MATCHES.
        // So I remove the validation check here!

        onMatch(selectedWord, meaning);
        setSelectedWord(null);
    };

    // Helper to find if a matched pair is correct (for display after submit)
    const isMatchCorrect = (word: string, meaning: string) => {
        const pair = allPairs.find(p => getWord(p) === word);
        return pair?.meaning === meaning;
    };

    const isWordMatched = (word: string) => matches[word] !== undefined;
    const isMeaningMatched = (meaning: string) => Object.values(matches).includes(meaning);

    const getWordColumnLabel = () => language === 'chinese' ? 'Chinese' : 'Word';
    const getMeaningColumnLabel = () => 'Meaning';

    if (!exercises || exercises.length === 0 || allPairs.length === 0) return null;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-purple-500 text-white flex items-center justify-center text-sm font-bold">
                        🔗
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800">Match the Pairs</h3>
                </div>
                {!isSubmitted && (
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-500">
                            {Object.keys(matches).length} / {allPairs.length} matched
                        </span>
                        {onReset && (
                            <button
                                onClick={onReset}
                                className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors"
                                title="Reset / Shuffle"
                            >
                                <Shuffle className="w-4 h-4 text-slate-600" />
                            </button>
                        )}
                    </div>
                )}
            </div>

            <div className="grid grid-cols-2 gap-6">
                {/* Word Column */}
                <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">{getWordColumnLabel()}</div>
                    {allPairs.map((pair, index) => {
                        const word = getWord(pair);
                        const matchedMeaning = matches[word];
                        const isMatched = !!matchedMeaning;
                        const isSelected = selectedWord === word;

                        // Result styling
                        let btnClass = isSelected
                            ? 'bg-purple-100 border-purple-500 ring-2 ring-purple-300'
                            : 'bg-white border-slate-200 hover:border-purple-400 hover:bg-purple-50';

                        if (isSubmitted && isMatched) {
                            const correct = isMatchCorrect(word, matchedMeaning);
                            btnClass = correct
                                ? 'bg-green-100 border-green-300 text-green-700'
                                : 'bg-red-100 border-red-300 text-red-700';
                        } else if (isMatched) {
                            btnClass = 'bg-blue-50 border-blue-300 text-blue-700';
                        }

                        return (
                            <button
                                key={index}
                                onClick={() => handleWordClick(word)}
                                disabled={isMatched || isSubmitted}
                                className={`w-full p-4 rounded-xl border-2 transition-all flex items-center justify-between ${btnClass}`}
                            >
                                <span className="text-xl font-bold">{word}</span>
                                <div onClick={(e) => { e.stopPropagation(); speak(word); }} className="p-2 rounded-full hover:bg-white/50 cursor-pointer">
                                    <Volume2 className="w-4 h-4 opacity-50" />
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Meaning Column */}
                <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">{getMeaningColumnLabel()}</div>
                    {shuffledMeanings.map((meaning, index) => {
                        const isMatched = isMeaningMatched(meaning);
                        // Find matching word for coloring results
                        const matchedWord = Object.keys(matches).find(w => matches[w] === meaning);

                        let btnClass = selectedWord
                            ? 'bg-white border-slate-200 hover:border-purple-400 hover:bg-purple-50 cursor-pointer'
                            : 'bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed';

                        if (isSubmitted && matchedWord) {
                            const correct = isMatchCorrect(matchedWord, meaning);
                            btnClass = correct
                                ? 'bg-green-100 border-green-300 text-green-700'
                                : 'bg-red-100 border-red-300 text-red-700';
                        } else if (isMatched) {
                            btnClass = 'bg-blue-50 border-blue-300 text-blue-700';
                        }

                        return (
                            <button
                                key={index}
                                onClick={() => handleMeaningClick(meaning)}
                                disabled={isMatched || !selectedWord || isSubmitted}
                                className={`w-full p-4 rounded-xl border-2 transition-all text-left ${btnClass}`}
                            >
                                <span className="text-lg">{meaning}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {!isSubmitted && (
                <p className="text-center text-sm text-slate-500">
                    Click a word (left), then click its meaning (right). You can assume any pair if not sure.
                </p>
            )}
        </div>
    );
}
