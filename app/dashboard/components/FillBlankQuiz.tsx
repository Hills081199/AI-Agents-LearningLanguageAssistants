"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, HelpCircle, Volume2 } from 'lucide-react';

// TTS language codes mapping
const TTS_CODES: Record<string, string> = {
    chinese: 'zh-CN',
    english: 'en-US',
    spanish: 'es-ES'
};

interface FillBlankExercise {
    type: 'fill_blank';
    sentence: string;
    answer: string;
    hint?: string;
    explanation?: string;
}

interface FillBlankQuizProps {
    exercises: FillBlankExercise[];
    language?: string;
}

export default function FillBlankQuiz({ exercises, language = 'chinese' }: FillBlankQuizProps) {
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [checked, setChecked] = useState<Record<number, boolean>>({});
    const [showHint, setShowHint] = useState<Record<number, boolean>>({});

    // Reset state when exercises change (new lesson)
    useEffect(() => {
        setAnswers({});
        setChecked({});
        setShowHint({});
    }, [exercises]);

    const handleInputChange = (index: number, value: string) => {
        if (checked[index]) return;
        setAnswers({ ...answers, [index]: value });
    };

    const checkAnswer = (index: number) => {
        setChecked({ ...checked, [index]: true });
    };

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = TTS_CODES[language] || 'en-US';
        utterance.rate = language === 'chinese' ? 0.8 : 0.9;
        speechSynthesis.speak(utterance);
    };

    const isCorrect = (index: number) => {
        const userAnswer = (answers[index] || '').trim().toLowerCase();
        const correctAnswer = exercises[index].answer.trim().toLowerCase();
        return userAnswer === correctAnswer;
    };

    if (!exercises || exercises.length === 0) {
        return null;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
                    ✏️
                </div>
                <h3 className="text-lg font-semibold text-slate-800">Fill in the Blank</h3>
            </div>

            {exercises.map((exercise, index) => {
                const isAnswerChecked = checked[index];
                const correct = isCorrect(index);

                // Split sentence by ___ to render input in the middle
                const parts = exercise.sentence.split('___');

                return (
                    <div
                        key={index}
                        className={`p-5 rounded-xl border-2 transition-all ${isAnswerChecked
                            ? correct
                                ? 'bg-green-50 border-green-300'
                                : 'bg-red-50 border-red-300'
                            : 'bg-white border-slate-200'
                            }`}
                    >
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                                #{index + 1}
                            </span>
                            {exercise.hint && (
                                <button
                                    onClick={() => setShowHint({ ...showHint, [index]: !showHint[index] })}
                                    className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
                                >
                                    <HelpCircle className="w-3 h-3" />
                                    Hint
                                </button>
                            )}
                        </div>

                        {/* Sentence with blank */}
                        <div className="text-xl text-slate-800 flex flex-wrap items-center gap-2 mb-4">
                            <span>{parts[0]}</span>
                            <input
                                type="text"
                                value={answers[index] || ''}
                                onChange={(e) => handleInputChange(index, e.target.value)}
                                disabled={isAnswerChecked}
                                placeholder="..."
                                className={`
                  w-32 px-3 py-2 text-center border-2 border-dashed rounded-lg text-lg font-medium
                  focus:outline-none focus:border-blue-500 transition-all
                  ${isAnswerChecked
                                        ? correct
                                            ? 'bg-green-100 border-green-400 text-green-700'
                                            : 'bg-red-100 border-red-400 text-red-700'
                                        : 'border-slate-300 bg-slate-50'
                                    }
                `}
                            />
                            <span>{parts[1] || ''}</span>

                            {/* TTS button for full sentence */}
                            <button
                                onClick={() => speak(exercise.sentence.replace('___', exercise.answer))}
                                className="p-2 rounded-full bg-slate-100 hover:bg-slate-200 transition-colors ml-2"
                                title="Listen"
                            >
                                <Volume2 className="w-4 h-4 text-slate-600" />
                            </button>
                        </div>

                        {/* Hint */}
                        {showHint[index] && exercise.hint && (
                            <div className="text-sm text-amber-700 bg-amber-50 p-2 rounded-lg mb-3">
                                💡 {exercise.hint}
                            </div>
                        )}

                        {/* Check button or result */}
                        {!isAnswerChecked ? (
                            <button
                                onClick={() => checkAnswer(index)}
                                disabled={!answers[index]?.trim()}
                                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Check Answer
                            </button>
                        ) : (
                            <div className="flex items-start gap-3">
                                {correct ? (
                                    <div className="flex items-center gap-2 text-green-600">
                                        <CheckCircle className="w-5 h-5" />
                                        <span className="font-medium">Correct!</span>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2 text-red-600">
                                            <XCircle className="w-5 h-5" />
                                            <span className="font-medium">Incorrect</span>
                                        </div>
                                        <div className="text-slate-600">
                                            Correct answer: <span className="font-bold text-green-600">{exercise.answer}</span>
                                        </div>
                                    </div>
                                )}
                                {exercise.explanation && (
                                    <div className="text-sm text-slate-500 ml-auto">
                                        {exercise.explanation}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
