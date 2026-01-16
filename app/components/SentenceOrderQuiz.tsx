"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Shuffle, Volume2, ArrowRight } from 'lucide-react';

interface SentenceOrderExercise {
    type: 'sentence_order';
    words: string[];
    answer: string;
    translation?: string;
}

interface SentenceOrderQuizProps {
    exercises: SentenceOrderExercise[];
}

export default function SentenceOrderQuiz({ exercises }: SentenceOrderQuizProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedWords, setSelectedWords] = useState<string[]>([]);
    const [availableWords, setAvailableWords] = useState<string[]>([]);
    const [checked, setChecked] = useState(false);
    const [results, setResults] = useState<Record<number, boolean>>({});

    const currentExercise = exercises[currentIndex];

    useEffect(() => {
        // Reset and shuffle when index OR exercises change
        if (currentExercise) {
            const shuffled = [...currentExercise.words].sort(() => Math.random() - 0.5);
            setAvailableWords(shuffled);
            setSelectedWords([]);
            setChecked(false);
            setResults({}); // Clear results if it's a new lesson start
        }
        // If it's a new lesson (exercises changed), reset index too
    }, [currentIndex, currentExercise]);

    // Reset index when exercises change (new lesson)
    useEffect(() => {
        setCurrentIndex(0);
        setResults({});
    }, [exercises]);

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    const handleWordClick = (word: string, fromSelected: boolean) => {
        if (checked) return;

        if (fromSelected) {
            setSelectedWords(selectedWords.filter((_, i) => i !== selectedWords.indexOf(word)));
            setAvailableWords([...availableWords, word]);
        } else {
            setSelectedWords([...selectedWords, word]);
            setAvailableWords(availableWords.filter((_, i) => i !== availableWords.indexOf(word)));
        }
    };

    const checkAnswer = () => {
        const userAnswer = selectedWords.join('');
        const isCorrect = userAnswer === currentExercise.answer;
        setResults({ ...results, [currentIndex]: isCorrect });
        setChecked(true);
    };

    const nextExercise = () => {
        if (currentIndex < exercises.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    const resetCurrent = () => {
        const shuffled = [...currentExercise.words].sort(() => Math.random() - 0.5);
        setAvailableWords(shuffled);
        setSelectedWords([]);
        setChecked(false);
    };

    if (!exercises || exercises.length === 0) {
        return null;
    }

    const isCorrect = results[currentIndex];
    const allDone = Object.keys(results).length === exercises.length;
    const score = Object.values(results).filter(Boolean).length;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold">
                        📝
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800">Arrange the Sentence</h3>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500">
                        {currentIndex + 1} / {exercises.length}
                    </span>
                    <button
                        onClick={resetCurrent}
                        className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors"
                        title="Reset"
                    >
                        <Shuffle className="w-4 h-4 text-slate-600" />
                    </button>
                </div>
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-orange-400 to-amber-500 transition-all duration-300"
                    style={{ width: `${((currentIndex + (checked ? 1 : 0)) / exercises.length) * 100}%` }}
                />
            </div>

            {/* Translation hint */}
            {currentExercise.translation && (
                <div className="text-center text-slate-600 bg-slate-50 p-3 rounded-xl">
                    Translate: <span className="font-medium">{currentExercise.translation}</span>
                </div>
            )}

            {/* Selected words area */}
            <div className={`
        min-h-[80px] p-4 rounded-xl border-2 border-dashed flex flex-wrap gap-2 items-center justify-center
        ${checked
                    ? isCorrect
                        ? 'bg-green-50 border-green-300'
                        : 'bg-red-50 border-red-300'
                    : 'bg-slate-50 border-slate-300'
                }
      `}>
                {selectedWords.length === 0 ? (
                    <span className="text-slate-400">Click words below to build the sentence...</span>
                ) : (
                    selectedWords.map((word, index) => (
                        <button
                            key={index}
                            onClick={() => handleWordClick(word, true)}
                            disabled={checked}
                            className={`
                px-4 py-2 rounded-lg text-lg font-medium transition-all
                ${checked
                                    ? isCorrect
                                        ? 'bg-green-200 text-green-800'
                                        : 'bg-red-200 text-red-800'
                                    : 'bg-orange-100 text-orange-800 hover:bg-orange-200'
                                }
              `}
                        >
                            {word}
                        </button>
                    ))
                )}

                {selectedWords.length > 0 && (
                    <button
                        onClick={() => speak(selectedWords.join(''))}
                        className="p-2 rounded-full bg-white/50 hover:bg-white transition-colors ml-2"
                    >
                        <Volume2 className="w-4 h-4 text-slate-500" />
                    </button>
                )}
            </div>

            {/* Available words */}
            <div className="flex flex-wrap gap-2 justify-center min-h-[50px]">
                {availableWords.map((word, index) => (
                    <button
                        key={index}
                        onClick={() => handleWordClick(word, false)}
                        disabled={checked}
                        className="px-4 py-2 bg-white border-2 border-slate-200 rounded-lg text-lg font-medium 
                     hover:border-orange-400 hover:bg-orange-50 transition-all disabled:opacity-50"
                    >
                        {word}
                    </button>
                ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-center gap-4">
                {!checked ? (
                    <button
                        onClick={checkAnswer}
                        disabled={selectedWords.length !== currentExercise.words.length}
                        className="px-6 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-medium 
                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Check Answer
                    </button>
                ) : (
                    <div className="flex flex-col items-center gap-4">
                        <div className="flex items-center gap-3">
                            {isCorrect ? (
                                <div className="flex items-center gap-2 text-green-600">
                                    <CheckCircle className="w-6 h-6" />
                                    <span className="font-semibold">Correct!</span>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-2">
                                    <div className="flex items-center gap-2 text-red-600">
                                        <XCircle className="w-6 h-6" />
                                        <span className="font-semibold">Incorrect</span>
                                    </div>
                                    <div className="text-slate-600">
                                        Correct: <span className="font-bold text-green-600">{currentExercise.answer}</span>
                                        <button
                                            onClick={() => speak(currentExercise.answer)}
                                            className="p-1 ml-2 rounded-full hover:bg-slate-100"
                                        >
                                            <Volume2 className="w-4 h-4 text-slate-500" />
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {currentIndex < exercises.length - 1 ? (
                            <button
                                onClick={nextExercise}
                                className="px-6 py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-medium 
                         transition-colors flex items-center gap-2"
                            >
                                Next <ArrowRight className="w-4 h-4" />
                            </button>
                        ) : (
                            <div className="text-center p-4 bg-slate-100 rounded-xl">
                                <p className="font-semibold text-slate-700">Complete! Score: {score}/{exercises.length}</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
