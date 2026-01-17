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
}

export default function MatchingQuiz({ exercises, language = 'chinese' }: MatchingQuizProps) {
    const [selectedWord, setSelectedWord] = useState<string | null>(null);
    const [matches, setMatches] = useState<Record<string, string>>({});
    const [shuffledMeanings, setShuffledMeanings] = useState<string[]>([]);
    const [isComplete, setIsComplete] = useState(false);

    // Combine all pairs from all matching exercises
    const allPairs = exercises.flatMap(e => e.pairs);

    // Get word display (handle both hanzi and word fields)
    const getWord = (pair: MatchingPair) => pair.word || pair.hanzi || '';

    useEffect(() => {
        // Shuffle meanings on mount or when exercises change
        resetGame();
    }, [exercises]);

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = TTS_CODES[language] || 'en-US';
        utterance.rate = language === 'chinese' ? 0.8 : 0.9;
        speechSynthesis.speak(utterance);
    };

    const handleWordClick = (word: string) => {
        if (matches[word]) return; // Already matched
        setSelectedWord(word);
    };

    const handleMeaningClick = (meaning: string) => {
        if (!selectedWord) return;
        if (Object.values(matches).includes(meaning)) return; // Already used

        // Check if correct match
        const correctPair = allPairs.find(p => getWord(p) === selectedWord);
        if (correctPair && correctPair.meaning === meaning) {
            setMatches({ ...matches, [selectedWord]: meaning });
        }
        setSelectedWord(null);

        // Check if complete
        if (Object.keys(matches).length + 1 === allPairs.length) {
            setIsComplete(true);
        }
    };

    const resetGame = () => {
        setSelectedWord(null);
        setMatches({});
        setIsComplete(false);
        setShuffledMeanings(allPairs.map(p => p.meaning).sort(() => Math.random() - 0.5));
    };

    const isWordMatched = (word: string) => matches[word] !== undefined;
    const isMeaningMatched = (meaning: string) => Object.values(matches).includes(meaning);

    // Get display labels based on language
    const getWordColumnLabel = () => {
        switch (language) {
            case 'chinese': return 'Chinese';
            case 'spanish': return 'Spanish';
            default: return 'Word';
        }
    };

    const getMeaningColumnLabel = () => {
        switch (language) {
            case 'chinese': return 'English';
            case 'spanish': return 'English';
            default: return 'Meaning';
        }
    };

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
                {/* Word Column */}
                <div className="space-y-3">
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">{getWordColumnLabel()}</div>
                    {allPairs.map((pair, index) => {
                        const word = getWord(pair);
                        const isMatched = isWordMatched(word);
                        const isSelected = selectedWord === word;

                        return (
                            <button
                                key={index}
                                onClick={() => handleWordClick(word)}
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
                                <span className="text-xl font-bold">{word}</span>
                                <button
                                    onClick={(e) => { e.stopPropagation(); speak(word); }}
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
                    <div className="text-sm font-medium text-slate-500 text-center mb-2">{getMeaningColumnLabel()}</div>
                    {shuffledMeanings.map((meaning, index) => {
                        const isMatched = isMeaningMatched(meaning);

                        return (
                            <button
                                key={index}
                                onClick={() => handleMeaningClick(meaning)}
                                disabled={isMatched || !selectedWord}
                                className={`
                  w-full p-4 rounded-xl border-2 transition-all text-left
                  ${isMatched
                                        ? 'bg-green-100 border-green-300 text-green-700'
                                        : selectedWord
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
                Click a word, then click its meaning to match.
            </p>
        </div>
    );
}
