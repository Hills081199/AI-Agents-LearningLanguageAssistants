"use client";

import { useState, useMemo } from 'react';
import { CheckCircle, XCircle, RotateCcw, ListChecks, PenLine, Link2, ArrowUpDown, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
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
    story?: string;
    language?: string;
    apiBaseUrl?: string;
    authApiUrl?: string;
    lessonFilename?: string;
    initialHistory?: any[];
}

// Multiple Choice Component (Controlled)
function MultipleChoiceQuiz({ questions, answers, onAnswer, isSubmitted }: {
    questions: QuizQuestion[],
    answers: Record<number, string>,
    onAnswer: (index: number, val: string) => void,
    isSubmitted: boolean
}) {
    return (
        <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center text-sm font-bold">
                    <ListChecks className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-semibold text-slate-800">Multiple Choice</h3>
            </div>

            {questions.map((q, qIndex) => {
                const userAnswer = answers[qIndex];
                const isSelected = !!userAnswer;
                const isCorrect = isSubmitted && userAnswer === q.answer;
                const isWrong = isSubmitted && userAnswer !== q.answer;

                let containerClass = "bg-white border-slate-200";
                if (isSubmitted) {
                    if (isCorrect) containerClass = "bg-green-50 border-green-200";
                    else if (isWrong) containerClass = "bg-red-50 border-red-200";
                }

                return (
                    <div key={qIndex} className={`p-6 rounded-xl border-2 transition-all ${containerClass}`}>
                        <div className="flex items-start gap-3 mb-4">
                            <span className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center text-sm font-bold">
                                {qIndex + 1}
                            </span>
                            <p className="text-lg text-slate-800 font-medium">{q.question}</p>
                        </div>

                        <div className="space-y-2 ml-11">
                            {q.options?.map((option, oIndex) => {
                                const optionLetter = option.charAt(0);
                                const isOptionSelected = userAnswer === optionLetter;
                                const isCorrectOption = q.answer === optionLetter;

                                let btnClass = "bg-white border-slate-200 hover:border-teal-400 hover:bg-teal-50 cursor-pointer";
                                if (isSubmitted) {
                                    if (isCorrectOption) btnClass = "bg-green-100 border-green-400 text-green-800";
                                    else if (isOptionSelected && !isCorrectOption) btnClass = "bg-red-100 border-red-400 text-red-800";
                                    else btnClass = "bg-slate-50 border-slate-200 text-slate-400 opacity-60";
                                } else {
                                    if (isOptionSelected) btnClass = "bg-indigo-50 border-indigo-500 text-indigo-700 shadow-sm ring-1 ring-indigo-500";
                                }

                                return (
                                    <button
                                        key={oIndex}
                                        onClick={() => !isSubmitted && onAnswer(qIndex, optionLetter)}
                                        disabled={isSubmitted}
                                        className={`w-full text-left p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${btnClass}`}
                                    >
                                        <span className="flex-1">{option}</span>
                                        {isSubmitted && isCorrectOption && <CheckCircle className="w-5 h-5 text-green-600" />}
                                        {isSubmitted && isOptionSelected && !isCorrectOption && <XCircle className="w-5 h-5 text-red-600" />}
                                    </button>
                                );
                            })}
                        </div>

                        {isSubmitted && q.explanation && (
                            <div className={`mt-4 ml-11 p-4 rounded-lg ${isCorrect ? 'bg-green-100/50' : 'bg-amber-100/50'}`}>
                                <p className="text-sm text-slate-700"><span className="font-semibold">Explanation:</span> {q.explanation}</p>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

// Main Quiz Component
export default function Quiz({ questions, story, language = 'chinese', apiBaseUrl, authApiUrl, lessonFilename, initialHistory }: QuizProps) {
    const [activeType, setActiveType] = useState<string>('all');
    const [showStory, setShowStory] = useState(false);
    const [history, setHistory] = useState<any[]>(initialHistory || []);
    const [showHistory, setShowHistory] = useState(false);

    // Global Quiz State
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    // Section States
    const [mcqAnswers, setMcqAnswers] = useState<Record<number, string>>({});
    const [fillBlankAnswers, setFillBlankAnswers] = useState<Record<number, string>>({});
    const [matchingAnswers, setMatchingAnswers] = useState<Record<string, string>>({});
    const [sentenceOrderAnswers, setSentenceOrderAnswers] = useState<Record<number, string[]>>({});

    // Group exercises
    const grouped = useMemo(() => {
        const mcq = questions.filter(q => q.type === 'multiple_choice' || (!q.type && q.options));
        const fillBlank = questions.filter(q => q.type === 'fill_blank');
        const matching = questions.filter(q => q.type === 'matching');
        const sentenceOrder = questions.filter(q => q.type === 'sentence_order');
        return { mcq, fillBlank, matching, sentenceOrder };
    }, [questions]);

    const totalCount = questions.length;

    // Derived Scores
    const result = useMemo(() => {
        let score = 0;
        let maxScore = questions.length; // Is it simply question length? Or items count?
        // MCQ: 1 point each
        grouped.mcq.forEach((q, i) => { if (mcqAnswers[i] === q.answer) score++; });

        // FillBlank: 1 point each
        grouped.fillBlank.forEach((q, i) => {
            const userFn = (fillBlankAnswers[i] || '').trim().toLowerCase();
            if (q.answer && userFn === q.answer.trim().toLowerCase()) score++;
        });

        // SentenceOrder: 1 point each
        grouped.sentenceOrder.forEach((q, i) => {
            const joiner = language === 'chinese' ? '' : ' ';
            const userStr = (sentenceOrderAnswers[i] || []).join(joiner);
            if (userStr === q.answer) score++;
        });

        // Matching: Is it 1 point per pair? Or 1 point per Exercise?
        // MatchingQuiz iterates `allPairs`.
        // Usually matching exercise counts as 1 question in `questions` array?
        // Let's check `grouped.matching`. It's an array of MatchingExercise.
        // Each Exercise has `pairs`.
        // If we count total items in `questions`, matching is 1 item.
        // But it has checks underneath? 
        // If we want detailed scoring, we should sum pairs?
        // But `maxScore = questions.length` implies 1 item = 1 point.
        // Let's award 1 point if ALL pairs in the exercise are correct?
        // OR award partial points?
        // Let's stick to 1 point per `question` item for simplicity and consistency with `questions.length`.

        grouped.matching.forEach((ex) => {
            // Check if all pairs in this exercise are matched correctly
            const allPairs = ex.pairs || [];
            const allCorrect = allPairs.every(p => {
                const w = p.word || p.hanzi || '';
                return matchingAnswers[w] === p.meaning;
            });
            if (allCorrect && allPairs.length > 0) score++;
        });

        return { score, maxScore };
    }, [questions, grouped, mcqAnswers, fillBlankAnswers, sentenceOrderAnswers, matchingAnswers, language]);

    const handleReset = () => {
        setMcqAnswers({});
        setFillBlankAnswers({});
        setMatchingAnswers({});
        setSentenceOrderAnswers({});
        setIsSubmitted(false);
    };

    const handleGlobalSubmit = async () => {
        setIsSubmitted(true);
        await saveGlobalProgress();
    };

    const saveGlobalProgress = async () => {
        if (!lessonFilename || !authApiUrl) return;
        setIsSaving(true);
        try {
            const token = localStorage.getItem("auth_token");
            const { score, maxScore } = result;

            // Flatten data for detailed storage
            const dataPayload = {
                mcq: mcqAnswers,
                fillBlank: fillBlankAnswers,
                matching: matchingAnswers,
                sentenceOrder: sentenceOrderAnswers
            };

            const payload = {
                lesson_id: lessonFilename,
                activity_type: 'quiz_full', // Changed type to distinguish
                score: score,
                max_score: maxScore,
                topic: 'Full Lesson Quiz',
                data: dataPayload
            };

            const res = await fetch(`${authApiUrl}/sessions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const session = await res.json();
                // Replace history with the latest single session
                setHistory([session]);
            } else {
                console.error("Failed to save session", res.status, await res.text());
            }
        } catch (e) {
            console.error(e);
        } finally {
            setIsSaving(false);
        }
    };

    if (!questions || questions.length === 0) return <div className="text-center py-12 text-slate-400">No exercises</div>;

    const quizTypes = [
        { key: 'all', label: 'All', icon: ListChecks, count: totalCount },
        { key: 'mcq', label: 'Multiple Choice', icon: ListChecks, count: grouped.mcq.length },
        { key: 'fillBlank', label: 'Fill Blank', icon: PenLine, count: grouped.fillBlank.length },
        { key: 'matching', label: 'Matching', icon: Link2, count: grouped.matching.length },
        { key: 'sentenceOrder', label: 'Word Order', icon: ArrowUpDown, count: grouped.sentenceOrder.length },
    ].filter(t => t.key === 'all' || t.count > 0);

    return (
        <div className="space-y-6">
            {/* Story Section */}
            {story && (
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                    <button onClick={() => setShowStory(!showStory)} className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center"><BookOpen className="w-5 h-5" /></div>
                            <div className="text-left"><h3 className="font-semibold text-slate-800">Reading Context</h3></div>
                        </div>
                        {showStory ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                    </button>
                    {showStory && (
                        <div className="p-6 pt-0 border-t border-slate-100 animate-in slide-in-from-top-2 duration-200">
                            <div className="prose prose-slate max-w-none whitespace-pre-wrap text-slate-700 leading-relaxed font-serif text-lg bg-slate-50 p-6 rounded-xl">
                                {story}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Type Selector */}
            <div className="flex flex-wrap gap-2 p-1 bg-slate-100 rounded-xl">
                {quizTypes.map(({ key, label, icon: Icon, count }) => (
                    <button
                        key={key}
                        onClick={() => setActiveType(key)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeType === key
                            ? 'bg-white shadow-sm text-teal-600'
                            : 'text-slate-600 hover:text-slate-800'}`}
                    >
                        <Icon className="w-4 h-4" /> {label} <span className={`text-xs px-1.5 py-0.5 rounded-full ${activeType === key ? 'bg-teal-100 text-teal-700' : 'bg-slate-200 text-slate-500'}`}>{count}</span>
                    </button>
                ))}
            </div>

            {/* Content Areas */}
            <div className="space-y-8">
                {(activeType === 'all' || activeType === 'mcq') && grouped.mcq.length > 0 && (
                    <MultipleChoiceQuiz
                        questions={grouped.mcq}
                        answers={mcqAnswers}
                        onAnswer={(idx, val) => setMcqAnswers(prev => ({ ...prev, [idx]: val }))}
                        isSubmitted={isSubmitted}
                    />
                )}
                {(activeType === 'all' || activeType === 'fillBlank') && grouped.fillBlank.length > 0 && (
                    <FillBlankQuiz
                        exercises={grouped.fillBlank as any}
                        language={language}
                        answers={fillBlankAnswers}
                        onAnswer={(idx, val) => setFillBlankAnswers(prev => ({ ...prev, [idx]: val }))}
                        isSubmitted={isSubmitted}
                    />
                )}
                {(activeType === 'all' || activeType === 'matching') && grouped.matching.length > 0 && (
                    <MatchingQuiz
                        exercises={grouped.matching as any}
                        language={language}
                        matches={matchingAnswers}
                        onMatch={(w, m) => setMatchingAnswers(prev => ({ ...prev, [w]: m }))}
                        isSubmitted={isSubmitted}
                        onReset={() => setMatchingAnswers({})}
                    />
                )}
                {(activeType === 'all' || activeType === 'sentenceOrder') && grouped.sentenceOrder.length > 0 && (
                    <SentenceOrderQuiz
                        exercises={grouped.sentenceOrder as any}
                        language={language}
                        answers={sentenceOrderAnswers}
                        onAnswer={(idx, val) => setSentenceOrderAnswers(prev => ({ ...prev, [idx]: val }))}
                        isSubmitted={isSubmitted}
                    />
                )}
            </div>

            {/* Global Submit Action */}
            <div className="sticky bottom-6 flex justify-center pt-8 pb-4">
                {!isSubmitted ? (
                    <button
                        onClick={handleGlobalSubmit}
                        disabled={isSaving}
                        className="px-10 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-bold text-lg shadow-xl hover:shadow-indigo-500/25 transition-all transform hover:scale-105 active:scale-95 flex items-center gap-3"
                    >
                        {isSaving ? "Submitting..." : "Submit All & Check Results"}
                        {!isSaving && <ListChecks className="w-5 h-5" />}
                    </button>
                ) : (
                    <div className="flex flex-col items-center gap-4 w-full animate-in fade-in slide-in-from-bottom-4">
                        <div className={`p-6 rounded-2xl border-2 w-full max-w-2xl text-center ${result.score === result.maxScore ? 'bg-green-50 border-green-200' : 'bg-slate-50 border-slate-200'}`}>
                            <h3 className="text-2xl font-bold text-slate-800 mb-2">Quiz Complete!</h3>
                            <div className="text-4xl font-black bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent mb-2">
                                {result.score} / {result.maxScore}
                            </div>
                            <p className="text-slate-600">
                                {result.score === result.maxScore ? "Perfect Score! 🎉" : "Great effort! Review your answers above."}
                            </p>
                        </div>
                        <button onClick={handleReset} className="px-6 py-3 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium flex items-center gap-2">
                            <RotateCcw className="w-4 h-4" /> Try Again
                        </button>
                    </div>
                )}
            </div>

            {/* History Section - Adjusted to show Latest Result only */}
            {history.length > 0 && (
                <div className="mt-12 border-t border-slate-200 pt-8">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">Latest Result</h3>
                    </div>

                    {/* Show only the first item (latest) */}
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center justify-between">
                        <div>
                            <div className="text-sm font-bold text-slate-700">{history[0].topic || "Quiz"}</div>
                            <div className="text-xs text-slate-500">{new Date((history[0].timestamp || history[0].created_at || Date.now() / 1000) * 1000).toLocaleString()}</div>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-bold ${(history[0].score / history[0].max_score) >= 0.8 ? 'bg-green-100 text-green-700' : (history[0].score / history[0].max_score) >= 0.5 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
                            {history[0].score} / {history[0].max_score}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
