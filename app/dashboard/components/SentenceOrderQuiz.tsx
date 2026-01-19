"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Shuffle, Volume2, ArrowRight, RotateCcw } from 'lucide-react';

// TTS language codes
const TTS_CODES: Record<string, string> = {
    chinese: 'zh-CN',
    english: 'en-US',
    spanish: 'es-ES'
};

interface SentenceOrderExercise {
    type: 'sentence_order';
    words: string[];
    answer: string;
    translation?: string;
}

interface SentenceOrderQuizProps {
    exercises: SentenceOrderExercise[];
    language?: string;
    answers: Record<number, string[]>; // index -> array of selected words in order
    onAnswer: (index: number, value: string[]) => void;
    isSubmitted: boolean;
}

export default function SentenceOrderQuiz({ exercises, language = 'chinese', answers, onAnswer, isSubmitted }: SentenceOrderQuizProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    // UI state for available words needed for drag/drop or click paradigm.
    // Since available words depend on selected words, and selected words are now in props (answers),
    // we must derive available words from (all words - selected words).

    // BUT: "all words - selected words" is ambiguous if a word appears twice.
    // We should track INDICES of used words if duplicates matter?
    // Assuming simple string filtering for now, or better:
    // Store `availableWords` in local state?
    // If we only store `answers` (selected words) in parent...
    // When we mount/change index, we init available words.
    // When we select a word, we remove it from available.
    // When we deselect, add back.
    // If strict state lifting: parent holds everything.
    // But `availableWords` is transient UI state.
    // Let's keep `availableWords` local, initialized from (exercise.words - answers[index]).

    const currentExercise = exercises[currentIndex];
    const currentSelected = answers[currentIndex] || [];

    // We need logic to track WHICH instances of words are available.
    // Simplest: `availableWords` state.
    const [availableWords, setAvailableWords] = useState<string[]>([]);

    useEffect(() => {
        if (!currentExercise) return;
        // Logic to sync available words when index changes or answers change externally (reset)
        // If no answer yet, all available.
        // If answer exists, remove those from available.
        // BUT how to handle shuffling?
        // We shuffle initially.
        // If we revisit a question, we want to see remaining available words.
        // Implementation detail: If we rely on simple string removal, fine.

        // Initial shuffle
        const all = [...currentExercise.words]; // Copy array
        // Remove currently selected items (by counting instances to handle duplicates)
        const counts = all.reduce((acc, w) => { acc[w] = (acc[w] || 0) + 1; return acc; }, {} as Record<string, number>);
        currentSelected.forEach(w => {
            if (counts[w] > 0) counts[w]--;
        });

        // Construct available based on remaining counts
        // Ideally we want to preserve shuffle order if possible?
        // Just recreate available list
        const remaining: string[] = [];
        // Iterate over a shuffled version of ALL to pick remaining?
        // Or just take what we have.
        // Let's just create a pool and remove.

        // Correct approach: 
        // We need a stable list of available words.
        // If `answers` update comes from `handleWordClick`, we manage `availableWords` locally too.

    }, [currentIndex, currentExercise, /* dependency on answers? causes loop if we update state */]);

    // Better approach:
    // Initialize availableWords on Mount/IndexChange with SHUFFLED FULL LIST.
    // Filter availableWords at RENDER time by removing `currentSelected`.
    // Wait, if duplicates exist ("the", "the"), removing "the" removes all? No.
    // We need unique IDs for words? Or index tracking.
    // Since API provides string[], we don't have IDs.
    // We'll manage `availableWords` state explicitly.

    // Init available when entering a question (if empty answer)
    useEffect(() => {
        if (currentExercise && currentSelected.length === 0) {
            setAvailableWords([...currentExercise.words].sort(() => Math.random() - 0.5));
        } else if (currentExercise) {
            // If revisiting and has answer, we need to reconstruct `available`?
            // It's hard without tracking "which specific word instance was moved".
            // Simplified: Available = All words - Selected. 
            // We can do this diffing.
            const remaining = [...currentExercise.words];
            currentSelected.forEach(sel => {
                const idx = remaining.indexOf(sel);
                if (idx > -1) remaining.splice(idx, 1);
            });
            setAvailableWords(remaining);
        }
    }, [currentIndex, currentExercise?.words]); // Don't depend on currentSelected to avoid loop, we update manually

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = TTS_CODES[language] || 'en-US';
        utterance.rate = language === 'chinese' ? 0.8 : 0.9;
        speechSynthesis.speak(utterance);
    };

    const handleWordSelect = (word: string) => {
        if (isSubmitted) return;
        // Move from available to selected
        const newSelected = [...currentSelected, word];
        onAnswer(currentIndex, newSelected);

        // Remove one instance from available
        const idx = availableWords.indexOf(word);
        if (idx > -1) {
            const newAvailable = [...availableWords];
            newAvailable.splice(idx, 1);
            setAvailableWords(newAvailable);
        }
    };

    const handleWordDeselect = (word: string) => {
        if (isSubmitted) return;
        // Move from selected to available
        const idx = currentSelected.lastIndexOf(word); // Remove last added instance? Or specific click?
        // We don't know which index was clicked if we just pass string. 
        // Ideally UI handles this.
        // Let's assume removing the specific instance clicked.
        // But `answers` is string[].
        // We'll remove the first instance of `word` in selected? Or last?
        // Let's remove the LAST instance to act like a stack?
        // Actually, user clicks a word in the "Selected" area.

        // Simplified: Remove the word from selected array.
        // Add to available array.
        const newSelected = [...currentSelected];
        const indexToRemove = newSelected.indexOf(word); // First instance
        if (indexToRemove > -1) {
            newSelected.splice(indexToRemove, 1);
            onAnswer(currentIndex, newSelected);
            setAvailableWords([...availableWords, word]);
        }
    };

    const resetCurrent = () => {
        if (isSubmitted) return;
        onAnswer(currentIndex, []);
        setAvailableWords([...currentExercise.words].sort(() => Math.random() - 0.5));
    }

    const nextExercise = () => {
        if (currentIndex < exercises.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    // Compute result for current index
    const joiner = language === 'chinese' ? '' : ' ';
    const userAnswerStr = currentSelected.join(joiner);
    const isCorrect = userAnswerStr === currentExercise.answer;

    if (!exercises || exercises.length === 0) return null;

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
                    {!isSubmitted && (
                        <button onClick={resetCurrent} className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors">
                            <RotateCcw className="w-4 h-4 text-slate-600" />
                        </button>
                    )}
                </div>
            </div>

            {/* Pagination / Progress */}
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden mb-4">
                <div className="h-full bg-orange-400 transition-all duration-300" style={{ width: `${((currentIndex + 1) / exercises.length) * 100}%` }} />
            </div>

            {currentExercise.translation && (
                <div className="text-center text-slate-600 bg-slate-50 p-3 rounded-xl">
                    Translate: <span className="font-medium">{currentExercise.translation}</span>
                </div>
            )}

            {/* Selected Words Area */}
            <div className={`min-h-[80px] p-4 rounded-xl border-2 border-dashed flex flex-wrap gap-2 items-center justify-center 
                ${isSubmitted
                    ? isCorrect ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'
                    : 'bg-slate-50 border-slate-300'}`}>

                {currentSelected.length === 0 ? (
                    <span className="text-slate-400">Click words below to build...</span>
                ) : (
                    currentSelected.map((word, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleWordDeselect(word)}
                            disabled={isSubmitted}
                            className={`px-4 py-2 rounded-lg text-lg font-medium transition-all ${isSubmitted
                                ? isCorrect ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                                : 'bg-orange-100 text-orange-800 hover:bg-orange-200 cursor-pointer'}`}
                        >
                            {word}
                        </button>
                    ))
                )}
                {currentSelected.length > 0 && (
                    <button onClick={() => speak(currentSelected.join(joiner))} className="p-2 rounded-full bg-white/50 hover:bg-white ml-2">
                        <Volume2 className="w-4 h-4 text-slate-500" />
                    </button>
                )}
            </div>

            {/* Available Words Area */}
            <div className="flex flex-wrap gap-2 justify-center min-h-[50px]">
                {availableWords.map((word, idx) => (
                    <button
                        key={idx}
                        onClick={() => handleWordSelect(word)}
                        disabled={isSubmitted}
                        className="px-4 py-2 bg-white border-2 border-slate-200 rounded-lg text-lg font-medium hover:border-orange-400 hover:bg-orange-50 transition-all"
                    >
                        {word}
                    </button>
                ))}
            </div>

            {/* Footer Navigation or Feedback */}
            <div className="flex flex-col items-center gap-4 mt-6">
                {isSubmitted && (
                    <div className="text-center animate-in fade-in slide-in-from-bottom-2">
                        {isCorrect ? (
                            <div className="flex items-center gap-2 text-green-600 mb-2 justify-center">
                                <CheckCircle className="w-6 h-6" />
                                <span className="font-bold text-lg">Correct!</span>
                            </div>
                        ) : (
                            <div className="text-red-600 mb-2">
                                <div className="flex items-center gap-2 justify-center font-bold text-lg">
                                    <XCircle className="w-6 h-6" />
                                    <span>Incorrect</span>
                                </div>
                                <div className="text-slate-600 mt-1">
                                    Answer: <span className="font-bold text-green-600">{currentExercise.answer}</span>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Navigation buttons */}
                <div className="flex gap-4">
                    {currentIndex > 0 && (
                        <button onClick={() => setCurrentIndex(currentIndex - 1)} className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700">Prev</button>
                    )}
                    {currentIndex < exercises.length - 1 && (
                        <button
                            onClick={nextExercise}
                            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 text-white flex items-center gap-2"
                        >
                            Next <ArrowRight className="w-4 h-4" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
