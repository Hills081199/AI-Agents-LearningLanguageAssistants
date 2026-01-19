import { useState } from 'react';
import { PenTool, CheckCircle, RefreshCw, AlertCircle, BookOpen, Send, Target, GraduationCap } from 'lucide-react';

interface WritingExerciseProps {
    topic: string;
    level: string;
    language: string;
    apiBaseUrl: string;
    authApiUrl?: string;
    initialPrompt?: PromptData | null;
    lessonFilename?: string;
    initialHistory?: any[];
}

interface PromptData {
    prompt_type: string;
    title: string;
    question: string;
    context: string;
    requirements: string[];
    word_count_min: number;
    word_count_max: number;
}

interface GradeData {
    criteria_scores: {
        task_achievement: number;
        coherence_cohesion: number;
        organization: number;
        idea_development: number;
        language_accuracy: number;
    };
    total_score: number;
    overall_feedback: string;
    detailed_feedback: {
        strengths: string[];
        weaknesses: string[];
    };
    improvement_suggestions: string[];
}

export default function WritingExercise({ topic, level, language, apiBaseUrl, authApiUrl, initialPrompt, lessonFilename, initialHistory }: WritingExerciseProps) {
    const [prompt, setPrompt] = useState<PromptData | null>(initialPrompt || null);
    const [submission, setSubmission] = useState('');
    const [grade, setGrade] = useState<GradeData | null>(null);
    const [history, setHistory] = useState<any[]>(initialHistory || []);
    const [showHistory, setShowHistory] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const generatePrompt = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${apiBaseUrl}/writing/prompt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, level, language }),
            });

            if (!response.ok) throw new Error('Failed to generate prompt');

            const data = await response.json();
            setPrompt(data);
            setGrade(null);
            setSubmission('');
        } catch (err) {
            setError('Could not generate writing prompt. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const submitWriting = async () => {
        if (!submission.trim() || !prompt) return;

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${apiBaseUrl}/writing/grade`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    submission,
                    prompt: JSON.stringify(prompt),
                    language
                }),
            });

            if (!response.ok) throw new Error('Failed to grade submission');

            const data = await response.json();
            setGrade(data);

            // Save progress
            if (lessonFilename && authApiUrl) {
                try {
                    const token = localStorage.getItem("auth_token");
                    await fetch(`${authApiUrl}/lesson-history/${lessonFilename}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            writing_score: data.total_score
                        }),
                    });

                    // Update local history
                    setHistory(prev => [...prev, {
                        timestamp: Date.now() / 1000,
                        prompt,
                        submission,
                        grade: data
                    }]);
                } catch (e) {
                    console.error("Failed to save progress", e);
                }
            }
        } catch (err) {
            setError('Could not grade submission. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getWordCount = (text: string) => {
        return text.trim().split(/\s+/).filter(w => w.length > 0).length;
    };

    const getScoreColor = (score: number) => {
        if (score >= 18) return 'text-green-600';
        if (score >= 15) return 'text-blue-600';
        if (score >= 12) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="mb-8 text-center">
                <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-3">
                    <PenTool className="w-8 h-8 text-purple-600" />
                    Writing Practice
                </h2>
                <p className="text-gray-600">Practice your writing skills with AI-graded assignments</p>
            </div>

            {history.length > 0 && (
                <div className="mb-6 flex justify-end">
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="text-purple-600 font-medium hover:underline flex items-center gap-2"
                    >
                        {showHistory ? "Back to Practice" : `View History (${history.length})`}
                    </button>
                </div>
            )}

            {showHistory ? (
                <div className="space-y-8">
                    {history.map((item, idx) => (
                        <div key={idx} className="bg-gray-50 border border-gray-200 rounded-xl p-6">
                            <div className="flex justify-between items-center mb-4">
                                <span className="font-bold text-gray-700">Submission #{idx + 1}</span>
                                <span className="text-sm text-gray-500">{new Date(item.timestamp * 1000).toLocaleString()}</span>
                            </div>
                            <div className="mb-4">
                                <h4 className="font-bold text-sm text-gray-500 uppercase">Prompt</h4>
                                <p className="font-medium text-gray-800">{item.prompt.title}</p>
                            </div>
                            <div className="mb-4">
                                <h4 className="font-bold text-sm text-gray-500 uppercase">Your Text</h4>
                                <p className="text-gray-600 bg-white p-3 rounded border border-gray-200 italic">"{item.submission}"</p>
                            </div>
                            <div className="border-t border-gray-200 pt-4">
                                <div className="flex items-center gap-4">
                                    <div className="text-2xl font-bold text-purple-600">{item.grade.total_score}/100</div>
                                    <div className="text-sm text-gray-600">{item.grade.overall_feedback}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <>
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </div>
                    )}

                    {!prompt ? (
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                            <BookOpen className="w-16 h-16 text-purple-100 mx-auto mb-4" />
                            <h3 className="text-xl font-bold text-gray-800 mb-2">Ready to write?</h3>
                            <p className="text-gray-500 mb-8 max-w-md mx-auto">
                                Generate a unique writing prompt based on your current topic: <span className="font-semibold text-purple-600">"{topic}"</span>
                            </p>
                            <button
                                onClick={generatePrompt}
                                disabled={loading}
                                className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-8 rounded-full transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
                            >
                                {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <PenTool className="w-5 h-5" />}
                                Generate Prompt
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Prompt Card */}
                            <div className="bg-white rounded-xl shadow-sm border border-purple-100 p-6 relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
                                <div className="flex justify-between items-start mb-4">
                                    <span className="bg-purple-100 text-purple-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                                        {prompt.prompt_type}
                                    </span>
                                    <button
                                        onClick={generatePrompt}
                                        className="text-gray-400 hover:text-purple-600 transition-colors text-sm flex items-center gap-1"
                                    >
                                        <RefreshCw className="w-3 h-3" /> New Prompt
                                    </button>
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">{prompt.title}</h3>
                                <p className="text-gray-700 mb-4 font-medium">{prompt.question}</p>
                                <div className="bg-gray-50 p-4 rounded-lg mb-4 text-gray-600 text-sm italic">
                                    {prompt.context}
                                </div>
                                <div className="space-y-2">
                                    <h4 className="text-sm font-bold text-gray-700 uppercase tracking-wider">Requirements:</h4>
                                    <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                                        {prompt.requirements.map((req, i) => (
                                            <li key={i}>{req}</li>
                                        ))}
                                        <li>Length: {prompt.word_count_min}-{prompt.word_count_max} words</li>
                                    </ul>
                                </div>
                            </div>

                            {/* Writing Area */}
                            {!grade ? (
                                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="font-bold text-gray-700 flex items-center gap-2">
                                            <PenTool className="w-4 h-4" /> Your Response
                                        </h3>
                                        <span className={`text-sm font-medium ${getWordCount(submission) < prompt.word_count_min || getWordCount(submission) > prompt.word_count_max
                                            ? 'text-orange-500'
                                            : 'text-green-600'
                                            }`}>
                                            {getWordCount(submission)} words
                                        </span>
                                    </div>
                                    <textarea
                                        value={submission}
                                        onChange={(e) => setSubmission(e.target.value)}
                                        placeholder="Start writing here..."
                                        className="w-full h-64 p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-medium text-gray-700 leading-relaxed"
                                        spellCheck={false}
                                    />
                                    <div className="mt-6 flex justify-end">
                                        <button
                                            onClick={submitWriting}
                                            disabled={loading || !submission.trim()}
                                            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                        >
                                            {loading ? (
                                                <>
                                                    <RefreshCw className="w-5 h-5 animate-spin" /> Grading...
                                                </>
                                            ) : (
                                                <>
                                                    <Send className="w-5 h-5" /> Submit for Grading
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                /* Results Area */
                                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

                                    {/* Score Card */}
                                    <div className="bg-white rounded-xl shadow-lg border border-purple-100 p-6">
                                        <div className="flex flex-col md:flex-row gap-8 items-center">
                                            {/* Total Score Circle */}
                                            <div className="relative w-32 h-32 flex-shrink-0">
                                                <svg className="w-full h-full" viewBox="0 0 36 36">
                                                    <path
                                                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none"
                                                        stroke="#eee"
                                                        strokeWidth="3"
                                                    />
                                                    <path
                                                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                                        fill="none"
                                                        stroke={grade.total_score >= 80 ? "#10b981" : grade.total_score >= 60 ? "#3b82f6" : "#f59e0b"}
                                                        strokeWidth="3"
                                                        strokeDasharray={`${grade.total_score}, 100`}
                                                        className="animate-[spin_1s_ease-out_reverse]"
                                                    />
                                                </svg>
                                                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                                                    <span className="text-3xl font-bold text-gray-800">{grade.total_score}</span>
                                                    <span className="text-xs text-gray-500 block">/100</span>
                                                </div>
                                            </div>

                                            {/* Criteria Breakdown */}
                                            <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {Object.entries(grade.criteria_scores).map(([key, score]) => (
                                                    <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                                        <span className="text-sm font-medium text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                                                        <span className={`font-bold ${getScoreColor(score)}`}>{score}/20</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Feedback */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-green-50 rounded-xl p-6 border border-green-100">
                                            <h4 className="font-bold text-green-800 flex items-center gap-2 mb-4">
                                                <CheckCircle className="w-5 h-5" /> Strengths
                                            </h4>
                                            <ul className="space-y-2">
                                                {grade.detailed_feedback.strengths.map((item, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-green-700 text-sm">
                                                        <span className="mt-1.5 w-1.5 h-1.5 bg-green-400 rounded-full flex-shrink-0"></span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>

                                        <div className="bg-amber-50 rounded-xl p-6 border border-amber-100">
                                            <h4 className="font-bold text-amber-800 flex items-center gap-2 mb-4">
                                                <Target className="w-5 h-5" /> Areas for Improvement
                                            </h4>
                                            <ul className="space-y-2">
                                                {grade.detailed_feedback.weaknesses.map((item, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-amber-700 text-sm">
                                                        <span className="mt-1.5 w-1.5 h-1.5 bg-amber-400 rounded-full flex-shrink-0"></span>
                                                        {item}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>

                                    {/* Detailed & Suggestions */}
                                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                        <div className="mb-6">
                                            <h4 className="font-bold text-gray-800 mb-2">Overall Feedback</h4>
                                            <p className="text-gray-600 leading-relaxed">{grade.overall_feedback}</p>
                                        </div>

                                        <div>
                                            <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                                                <GraduationCap className="w-5 h-5 text-purple-600" /> Specific Suggestions
                                            </h4>
                                            <div className="bg-purple-50 rounded-lg p-4 space-y-3">
                                                {grade.improvement_suggestions.map((suggestion, i) => (
                                                    <div key={i} className="flex gap-3">
                                                        <span className="bg-purple-200 text-purple-700 font-bold w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                                                            {i + 1}
                                                        </span>
                                                        <p className="text-purple-900 text-sm pt-0.5">{suggestion}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex justify-center pt-4">
                                        <button
                                            onClick={() => { setGrade(null); }}
                                            className="text-purple-600 hover:text-purple-700 font-medium flex items-center gap-2 transition-colors"
                                        >
                                            <RefreshCw className="w-4 h-4" /> Revise & Try Again
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
