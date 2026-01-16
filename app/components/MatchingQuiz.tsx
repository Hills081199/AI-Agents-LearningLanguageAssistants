"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, Shuffle, Volume2 } from 'lucide-react';

interface MatchingPair {
    hanzi: string;
    meaning: string;
}

interface MatchingExercise {
    type: 'matching';
    pairs: MatchingPair[];
}

interface MatchingQuizProps {
    exercises: MatchingExercise[];
}

export default function MatchingQuiz({ exercises }: MatchingQuizProps) {
    const [selectedHanzi, setSelectedHanzi] = useState<string | null>(null);
    const [matches, setMatches] = useState<Record<string, string>>({});
    const [shuffledMeanings, setShuffledMeanings] = useState<string[]>([]);
    const [isComplete, setIsComplete] = useState(false);

    // Combine all pairs from all matching exercises
    const allPairs = exercises.flatMap(e => e.pairs);

    useEffect(() => {
        // Shuffle meanings on mount or when exercises change
        resetGame();
    }, [exercises]);

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    const handleHanziClick = (hanzi: string) => {
        if (matches[hanzi]) return; // Already matched
        setSelectedHanzi(hanzi);
    };

    const handleMeaningClick = (meaning: string) => {
        if (!selectedHanzi) return;
        if (Object.values(matches).includes(meaning)) return; // Already used

        // Check if correct match
        const correctPair = allPairs.find(p => p.hanzi === selectedHanzi);
        if (correctPair && correctPair.meaning === meaning) {
            setMatches({ ...matches, [selectedHanzi]: meaning });
        }
        setSelectedHanzi(null);

        // Check if complete
        if (Object.keys(matches).length + 1 === allPairs.length) {
            setIsComplete(true);
        }
    };

    const resetGame = () => {
        setSelectedHanzi(null);
        setMatches({});
        setIsComplete(false);
        setShuffledMeanings(allPairs.map(p => p.meaning).sort(() => Math.random() - 0.5));
    };

    const isHanziMatched = (hanzi: string) => matches[hanzi] !== undefined;
    const isMeaningMatched = (meaning: string) => Object.values(matches).includes(meaning);

    if (!exercises || exercises.length === 0 || allPairs.length === 0) {
        return null;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-purple-500 text-white flex items-center justify-center text-sm font-bold">
                        🔗
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800">Match the Pairs</h3>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-sm text-slate-500">
                        {Object.keys(matches).length} / {allPairs.length} matched
                    </span>
                    <button
                        onClick={resetGame}
                        className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors"
                        title="Shuffle"
                    >
                        <Shuffle className="w-4 h-4 text-slate-600" />
                    </button>
                </div>
            </div>

            {isComplete && (
                <div className="p-4 bg-gradient-to-r from-green-100 to-emerald-100 rounded-xl border border-green-200 text-center">
                    <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                    <p className="text-green-700 font-semibold">🎉 Perfect! All pairs matched!</p>
                </div>
            )}

            <div className="grid grid-cols-2 gap-6">
                {/* Hanzi Column */}
                <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">Chinese</div>
                    {allPairs.map((pair, index) => {
                        const isMatched = isHanziMatched(pair.hanzi);
                        const isSelected = selectedHanzi === pair.hanzi;

                        return (
                            <button
                                key={index}
                                onClick={() => handleHanziClick(pair.hanzi)}
                                disabled={isMatched}
                                className={`
                  w-full p-4 rounded-xl border-2 transition-all flex items-center justify-between
                  ${isMatched
                                        ? 'bg-green-100 border-green-300 text-green-700'
                                        : isSelected
                                            ? 'bg-purple-100 border-purple-500 ring-2 ring-purple-300'
                                            : 'bg-white border-slate-200 hover:border-purple-400 hover:bg-purple-50'
                                    }
                `}
                            >
                                <span className="text-xl font-bold">{pair.hanzi}</span>
                                <button
                                    onClick={(e) => { e.stopPropagation(); speak(pair.hanzi); }}
                                    className="p-2 rounded-full bg-white/50 hover:bg-white transition-colors"
                                >
                                    <Volume2 className="w-4 h-4 text-slate-500" />
                                </button>
                            </button>
                        );
                    })}
                </div>

                {/* Meaning Column */}
                <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">English</div>
                    {shuffledMeanings.map((meaning, index) => {
                        const isMatched = isMeaningMatched(meaning);

                        return (
                            <button
                                key={index}
                                onClick={() => handleMeaningClick(meaning)}
                                disabled={isMatched || !selectedHanzi}
                                className={`
                  w-full p-4 rounded-xl border-2 transition-all text-left
                  ${isMatched
                                        ? 'bg-green-100 border-green-300 text-green-700'
                                        : selectedHanzi
                                            ? 'bg-white border-slate-200 hover:border-purple-400 hover:bg-purple-50 cursor-pointer'
                                            : 'bg-slate-50 border-slate-200 text-slate-400 cursor-not-allowed'
                                    }
                `}
                            >
                                <span className="text-lg">{meaning}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            <p className="text-center text-sm text-slate-500">
                Click a Chinese word, then click its English meaning to match.
            </p>
        </div>
    );
}
