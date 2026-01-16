"use client";

import { useState, useMemo } from 'react';
import { CheckCircle, XCircle, RotateCcw, ListChecks, PenLine, Link2, ArrowUpDown } from 'lucide-react';
import FillBlankQuiz from './FillBlankQuiz';
import MatchingQuiz from './MatchingQuiz';
import SentenceOrderQuiz from './SentenceOrderQuiz';

interface QuizQuestion {
    type?: string;
    question?: string;
    options?: string[];
    answer?: string;
    explanation?: string;
    sentence?: string;
    hint?: string;
    pairs?: any[];
    words?: string[];
    translation?: string;
}

interface QuizProps {
    questions: QuizQuestion[];
}

// Multiple Choice Component (embedded)
function MultipleChoiceQuiz({ questions }: { questions: QuizQuestion[] }) {
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [showResults, setShowResults] = useState<Record<number, boolean>>({});

    const handleAnswer = (questionIndex: number, selectedLetter: string) => {
        if (showResults[questionIndex]) return;
        setAnswers({ ...answers, [questionIndex]: selectedLetter });
        setShowResults({ ...showResults, [questionIndex]: true });
    };

    const resetQuiz = () => {
        setAnswers({});
        setShowResults({});
    };

    const getScore = () => {
        let correct = 0;
        questions.forEach((q, i) => {
            if (answers[i] === q.answer) correct++;
        });
        return correct;
    };

    const allAnswered = Object.keys(showResults).length === questions.length;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center text-sm font-bold">
                        <ListChecks className="w-4 h-4" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-800">Multiple Choice</h3>
                </div>
                {allAnswered && (
                    <button
                        onClick={resetQuiz}
                        className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors"
                    >
                        <RotateCcw className="w-4 h-4" />
                        Retry
                    </button>
                )}
            </div>

            {allAnswered && (
                <div className={`p-6 rounded-xl text-center mb-6 ${getScore() === questions.length
                        ? 'bg-gradient-to-r from-green-100 to-emerald-100 border border-green-200'
                        : getScore() >= questions.length / 2
                            ? 'bg-gradient-to-r from-yellow-100 to-amber-100 border border-yellow-200'
                            : 'bg-gradient-to-r from-red-100 to-rose-100 border border-red-200'
                    }`}>
                    <div className="text-3xl font-bold mb-2">{getScore()} / {questions.length}</div>
                    <div className="text-slate-600">
                        {getScore() === questions.length ? '🎉 Perfect Score!' : getScore() >= questions.length / 2 ? '👍 Good Job!' : '📚 Keep Practicing!'}
                    </div>
                </div>
            )}

            {questions.map((q, qIndex) => {
                const userAnswer = answers[qIndex];
                const isAnswered = showResults[qIndex];
                const isCorrect = userAnswer === q.answer;

                return (
                    <div
                        key={qIndex}
                        className={`p-6 rounded-xl border-2 transition-all ${isAnswered ? isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200' : 'bg-white border-slate-200'
                            }`}
                    >
                        <div className="flex items-start gap-3 mb-4">
                            <span className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center text-sm font-bold">
                                {qIndex + 1}
                            </span>
                            <p className="text-lg text-slate-800 font-medium">{q.question}</p>
                        </div>

                        <div className="space-y-2 ml-11">
                            {q.options?.map((option, oIndex) => {
                                const optionLetter = option.charAt(0);
                                const isSelected = userAnswer === optionLetter;
                                const isCorrectOption = q.answer === optionLetter;

                                return (
                                    <button
                                        key={oIndex}
                                        onClick={() => handleAnswer(qIndex, optionLetter)}
                                        disabled={isAnswered}
                                        className={`w-full text-left p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${isAnswered
                                                ? isCorrectOption
                                                    ? 'bg-green-100 border-green-400 text-green-800'
                                                    : isSelected
                                                        ? 'bg-red-100 border-red-400 text-red-800'
                                                        : 'bg-slate-50 border-slate-200 text-slate-500'
                                                : 'bg-white border-slate-200 hover:border-teal-400 hover:bg-teal-50 cursor-pointer'
                                            }`}
                                    >
                                        <span className="flex-1">{option}</span>
                                        {isAnswered && isCorrectOption && <CheckCircle className="w-5 h-5 text-green-600" />}
                                        {isAnswered && isSelected && !isCorrectOption && <XCircle className="w-5 h-5 text-red-600" />}
                                    </button>
                                );
                            })}
                        </div>

                        {isAnswered && q.explanation && (
                            <div className={`mt-4 ml-11 p-4 rounded-lg ${isCorrect ? 'bg-green-100/50' : 'bg-amber-100/50'}`}>
                                <p className="text-sm text-slate-700">
                                    <span className="font-semibold">Explanation:</span> {q.explanation}
                                </p>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

// Main Quiz Router Component
export default function Quiz({ questions }: QuizProps) {
    const [activeType, setActiveType] = useState<string>('all');

    // Group exercises by type
    const grouped = useMemo(() => {
        const mcq = questions.filter(q => q.type === 'multiple_choice' || (!q.type && q.options));
        const fillBlank = questions.filter(q => q.type === 'fill_blank');
        const matching = questions.filter(q => q.type === 'matching');
        const sentenceOrder = questions.filter(q => q.type === 'sentence_order');
        return { mcq, fillBlank, matching, sentenceOrder };
    }, [questions]);

    const totalCount = questions.length;

    if (!questions || questions.length === 0) {
        return (
            <div className="text-center py-12 text-slate-400">
                <p>No exercises available for this lesson.</p>
            </div>
        );
    }

    const quizTypes = [
        { key: 'all', label: 'All', icon: ListChecks, count: totalCount },
        { key: 'mcq', label: 'Multiple Choice', icon: ListChecks, count: grouped.mcq.length },
        { key: 'fillBlank', label: 'Fill Blank', icon: PenLine, count: grouped.fillBlank.length },
        { key: 'matching', label: 'Matching', icon: Link2, count: grouped.matching.length },
        { key: 'sentenceOrder', label: 'Word Order', icon: ArrowUpDown, count: grouped.sentenceOrder.length },
    ].filter(t => t.key === 'all' || t.count > 0);

    return (
        <div className="space-y-6">
            {/* Type Selector */}
            <div className="flex flex-wrap gap-2 p-1 bg-slate-100 rounded-xl">
                {quizTypes.map(({ key, label, icon: Icon, count }) => (
                    <button
                        key={key}
                        onClick={() => setActiveType(key)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeType === key
                                ? 'bg-white shadow-sm text-teal-600'
                                : 'text-slate-600 hover:text-slate-800'
                            }`}
                    >
                        <Icon className="w-4 h-4" />
                        {label}
                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${activeType === key ? 'bg-teal-100 text-teal-700' : 'bg-slate-200 text-slate-500'
                            }`}>
                            {count}
                        </span>
                    </button>
                ))}
            </div>

            {/* Quiz Content */}
            <div className="space-y-8">
                {(activeType === 'all' || activeType === 'mcq') && grouped.mcq.length > 0 && (
                    <MultipleChoiceQuiz questions={grouped.mcq} />
                )}

                {(activeType === 'all' || activeType === 'fillBlank') && grouped.fillBlank.length > 0 && (
                    <FillBlankQuiz exercises={grouped.fillBlank as any} />
                )}

                {(activeType === 'all' || activeType === 'matching') && grouped.matching.length > 0 && (
                    <MatchingQuiz exercises={grouped.matching as any} />
                )}

                {(activeType === 'all' || activeType === 'sentenceOrder') && grouped.sentenceOrder.length > 0 && (
                    <SentenceOrderQuiz exercises={grouped.sentenceOrder as any} />
                )}
            </div>
        </div>
    );
}
