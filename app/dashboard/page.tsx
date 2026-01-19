"use client";

import { useState, useEffect } from "react";
import { Sparkles, Loader2, BookOpen, GraduationCap, Target, Menu, X, ChevronRight, Zap, PlayCircle, Check, Circle, Dices, Crown, Globe, PenTool, LogOut } from "lucide-react";
import VocabularyList from "./components/VocabularyList";
import Quiz from "./components/Quiz";
import RoleplayChat from "./components/RoleplayChat";
import PricingModal from "./components/PricingModal";
import WritingExercise from "./components/WritingExercise";

interface LessonData {
  topic: string;
  level: string;
  language: string;
  story: string;
  vocabulary: any[];
  grammar: any[];
  quiz: any[];
  writing_prompt?: any;
  filename?: string;
  progress?: any;
}

interface HistoryItem {
  filename: string;
  topic: string;
  level?: string;
  language?: string;
  created_at: number;
}

interface LanguageConfig {
  code: string;
  name: string;
  native_name: string;
  levels: string[];
  level_system: string;
}

// Default language configurations (fallback if API fails)
const DEFAULT_LANGUAGES: LanguageConfig[] = [
  {
    code: "chinese",
    name: "Chinese",
    native_name: "中文",
    levels: ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"],
    level_system: "HSK"
  },
  {
    code: "english",
    name: "English",
    native_name: "English",
    levels: ["A1", "A2", "B1", "B2", "C1", "C2"],
    level_system: "CEFR"
  },
  {
    code: "spanish",
    name: "Spanish",
    native_name: "Español",
    levels: ["A1", "A2", "B1", "B2", "C1", "C2"],
    level_system: "CEFR"
  }
];

// Language flag emojis
const LANGUAGE_FLAGS: Record<string, string> = {
  chinese: "🇨🇳",
  english: "🇬🇧",
  spanish: "🇪🇸"
};

export default function Home() {
  const [language, setLanguage] = useState("chinese");
  const [languages, setLanguages] = useState<LanguageConfig[]>(DEFAULT_LANGUAGES);
  const [level, setLevel] = useState("HSK 3");
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [lessonData, setLessonData] = useState<LessonData | null>(null);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeView, setActiveView] = useState<"objectives" | "reading" | "quiz" | "writing">("objectives");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [suggesting, setSuggesting] = useState(false);

  const [loadingStep, setLoadingStep] = useState(0);
  const [showPricing, setShowPricing] = useState(false);

  // Determine API base URLs dynamically
  const [apiBaseUrl, setApiBaseUrl] = useState("http://127.0.0.1:8000"); // Agent Service
  const [authApiUrl, setAuthApiUrl] = useState("http://127.0.0.1:8001"); // Auth Service

  useEffect(() => {
    if (typeof window !== "undefined") {
      const host = window.location.hostname;
      if (host !== "localhost" && host !== "127.0.0.1") {
        setApiBaseUrl(`http://${host}:8000`);
        setAuthApiUrl(`http://${host}:8001`);
      }
    }
  }, []);

  // Fetch available languages from API
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/languages`);
        const data = await res.json();
        if (data && data.length > 0) {
          setLanguages(data);
        }
      } catch (e) {
        console.log("Using default language config");
      }
    };
    fetchLanguages();
  }, [apiBaseUrl]);

  useEffect(() => {
    fetchHistory();
  }, [authApiUrl, language]);

  // Update level when language changes
  useEffect(() => {
    const currentLangConfig = languages.find(l => l.code === language);
    if (currentLangConfig && currentLangConfig.levels.length > 0) {
      // Set to a middle level by default
      const midIndex = Math.floor(currentLangConfig.levels.length / 2);
      setLevel(currentLangConfig.levels[midIndex]);
    }
  }, [language, languages]);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    if (loading) {
      setLoadingStep(0);
      // Sequence of loading steps with variable durations
      const delays = [2000, 6000, 12000, 5000];

      let currentStep = 0;
      const runSequence = () => {
        if (currentStep < 4) {
          timeout = setTimeout(() => {
            currentStep++;
            setLoadingStep(currentStep);
            runSequence();
          }, delays[currentStep]);
        }
      };
      runSequence();
    }
    return () => clearTimeout(timeout);
  }, [loading]);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      if (!authApiUrl) {
        console.warn("fetchHistory: authApiUrl is missing");
        return;
      }

      const res = await fetch(`${authApiUrl}/lesson-history?language=${language.toLowerCase()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        console.log("Fetched history:", data.length, "items");
        // Map DB response to HistoryItem interface
        const formattedHistory = data.map((item: any) => ({
          ...item,
          filename: item.id, // Use ID as filename
          created_at: item.created_at ? new Date(item.created_at).getTime() / 1000 : Date.now() / 1000
        }));
        setHistory(formattedHistory);
      } else {
        console.error("Failed to fetch history:", await res.text());
      }
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  const loadLesson = async (filename: string) => { // Filename here is actually ID for history
    if (loading) return;
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      // If it looks like a legacy filename (ends in .html), use agent service
      if (filename.endsWith('.html')) {
        const res = await fetch(`${apiBaseUrl}/file-history/${filename}`);
        const data = await res.json();
        if (data.html_content) setHtmlContent(data.html_content);
        if (data.lesson_data) {
          setLessonData({
            ...data.lesson_data,
            filename: filename,
            progress: data.progress
          });
        }
      } else {
        // Load from DB via auth service
        const res = await fetch(`${authApiUrl}/lesson-history/${filename}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        if (data.lesson_content) {
          // Reconstruct lesson data from DB format
          const content = data.lesson_content;
          setLessonData({
            topic: content.topic,
            level: content.level,
            language: content.language,
            story: content.story,
            vocabulary: content.vocabulary,
            grammar: content.grammar,
            quiz: content.quiz,
            writing_prompt: content.writing_prompt,
            filename: data.id, // Use ID as filename reference
            progress: { writing_history: [] }
          });
          // Hybrid Loading: Try to fetch HTML content from Agent Service using original filename
          // This allows us to use the beautiful HTML format if the file still exists locally
          const originalFilename = content.filename;
          if (originalFilename) {
            try {
              const htmlRes = await fetch(`${apiBaseUrl}/file-history/${originalFilename}`);
              if (htmlRes.ok) {
                const htmlData = await htmlRes.json();
                if (htmlData.html_content) {
                  setHtmlContent(htmlData.html_content);
                } else {
                  setHtmlContent(null);
                }
              } else {
                setHtmlContent(null);
              }
            } catch (e) {
              console.warn("Failed to load HTML content from agent service", e);
              setHtmlContent(null);
            }
          } else {
            setHtmlContent(null);
          }
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const generateLesson = async () => {
    if (loading) return;
    setLoading(true);
    setLessonData(null);
    setHtmlContent(null);
    setActiveView("objectives");

    try {
      // 1. Generate Lesson (Agent Service)
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic || null, level, language }),
      });

      const data = await response.json();
      if (data.html_content) setHtmlContent(data.html_content);

      const newLessonData = {
        topic: data.topic,
        level: data.level,
        language: data.language || language,
        story: data.markdown_content,
        vocabulary: data.vocabulary || [],
        grammar: data.grammar || [],
        quiz: data.quiz || [],
        writing_prompt: data.writing_prompt || null,
        filename: data.filename, // Temporary filename from agent
        progress: null
      };

      setLessonData(newLessonData);

      // 2. Save to Database (Auth Service)
      try {
        const token = localStorage.getItem("auth_token");
        if (token && authApiUrl) {
          const saveResponse = await fetch(`${authApiUrl}/lesson-history`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
              topic: data.topic,
              level: data.level,
              language: (data.language || language).toLowerCase(),
              lesson_content: newLessonData
            })
          });

          if (saveResponse.ok) {
            const savedLesson = await saveResponse.json();
            // Update filename with real DB ID so progress saving works
            setLessonData({
              ...newLessonData,
              filename: savedLesson.id
            });
          } else {
            console.error("Save response not ok:", await saveResponse.text());
          }
        }
      } catch (saveError) {
        console.error("Failed to save lesson to history:", saveError);
      }

      fetchHistory();
    } catch (error) {
      console.error("Failed to generate lesson:", error);
    } finally {
      setLoading(false);
    }
  };

  const hasData = lessonData || htmlContent;
  const currentLangConfig = languages.find(l => l.code === language);
  const currentLevels = currentLangConfig?.levels || [];

  const navItems = [

    { key: "objectives", label: "Lesson Objectives", icon: Zap },
    { key: "reading", label: "Reading", icon: BookOpen },
    { key: "quiz", label: "Practice", icon: Target, count: lessonData?.quiz?.length },
    { key: "writing", label: "Writing", icon: PenTool },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* Sidebar - Glassmorphism Light */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 bg-white/80 backdrop-blur-xl border-r border-slate-200/60 transform transition-transform duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] shadow-xl shadow-slate-200/50 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="p-6 border-b border-slate-100 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">Language Factory</span>
          </div>

          {/* Generator Controls */}
          <div className="p-5 space-y-4 border-b border-slate-100 bg-slate-50/50">
            {/* Language Selector */}
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 block ml-1 flex items-center gap-1.5">
                <Globe className="w-3 h-3" />
                Language
              </label>
              <div className="grid grid-cols-3 gap-1.5">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => setLanguage(lang.code)}
                    disabled={loading}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all flex flex-col items-center gap-1 ${language === lang.code
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
                      : "bg-white border border-slate-200 text-slate-600 hover:border-indigo-300 hover:text-indigo-600"
                      }`}
                  >
                    <span className="text-lg">{LANGUAGE_FLAGS[lang.code] || "🌐"}</span>
                    <span>{lang.name}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 block ml-1">New Lesson</label>
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Enter a topic..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={loading}
                  className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm placeholder:text-slate-400"
                />
                <button
                  onClick={async () => {
                    if (loading || suggesting) return;
                    setSuggesting(true);
                    setTopic("Asking AI...");
                    try {
                      const res = await fetch(`${apiBaseUrl}/suggest-topic`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ level, language })
                      });
                      const data = await res.json();
                      if (data.topic) setTopic(data.topic);
                    } catch (e) {
                      setTopic("Travel");
                    } finally {
                      setSuggesting(false);
                    }
                  }}
                  disabled={loading || suggesting}
                  className="w-full py-2 bg-indigo-50 border border-indigo-100 text-indigo-600 rounded-xl hover:bg-indigo-100 hover:border-indigo-200 transition-all text-sm font-medium flex items-center justify-center gap-2"
                >
                  {suggesting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Dices className="w-4 h-4" />}
                  <span>Random Topic</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                disabled={loading}
                className="px-3 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 shadow-sm cursor-pointer hover:border-indigo-300 transition-colors"
              >
                {currentLevels.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              <button
                onClick={generateLesson}
                disabled={loading}
                className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-50 flex items-center gap-2 justify-center"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                <span>Generate</span>
              </button>
            </div>
          </div>

          {/* Library Section (History list) */}
          <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3 mt-2 flex items-center justify-between">
              <span>History</span>
              <span className="text-[10px] px-2 py-0.5 bg-slate-100 rounded-full">{LANGUAGE_FLAGS[language]} {currentLangConfig?.name}</span>
            </div>

            {loading && !hasData && (
              <div className="mb-2 px-4 py-3 bg-indigo-50/50 border border-indigo-100 rounded-xl flex items-center gap-3">
                <div className="w-4 h-4 rounded-full border-2 border-indigo-200 border-t-indigo-600 animate-spin" />
                <div className="flex flex-col gap-1">
                  <div className="h-2.5 bg-indigo-200/50 rounded w-20 animate-pulse" />
                  <div className="h-2 bg-indigo-100 rounded w-12 animate-pulse" />
                </div>
              </div>
            )}

            <div className="space-y-1">
              {history.length > 0 ? (
                history.map((item) => (
                  <button
                    key={item.filename}
                    onClick={() => loadLesson(item.filename)}
                    disabled={loading}
                    className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all group border border-transparent ${loading
                      ? "opacity-50 cursor-not-allowed"
                      : "hover:bg-white hover:shadow-md hover:shadow-slate-200/50 hover:border-slate-100 text-slate-600 hover:text-slate-900"
                      }`}
                  >
                    <div className="w-full">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium truncate pr-2 flex-1">{item.topic}</span>
                        {item.level && (
                          <span className="text-[9px] px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded font-bold uppercase tracking-wide whitespace-nowrap">
                            {item.level}
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-400 block">{new Date(item.created_at * 1000).toLocaleDateString()}</span>
                    </div>
                  </button>
                ))
              ) : (
                <div className="p-8 text-center">
                  <p className="text-xs text-slate-400">No {currentLangConfig?.name} lessons yet.</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/80 space-y-3">
            <button
              onClick={() => setShowPricing(true)}
              className="w-full py-4 px-4 bg-gradient-to-r from-amber-400 to-yellow-500 hover:from-amber-500 hover:to-yellow-600 text-white font-bold rounded-2xl shadow-xl shadow-amber-200/50 flex items-center justify-center gap-3 transition-all hover:-translate-y-1 group"
            >
              <Crown className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              <div className="text-left">
                <p className="text-[10px] uppercase opacity-80 leading-none mb-1">Premium</p>
                <p className="text-sm leading-none">Upgrade Plan</p>
              </div>
            </button>

            <button
              onClick={() => {
                localStorage.removeItem("auth_token");
                window.location.href = "/landing";
              }}
              className="w-full py-3 px-4 bg-white border border-slate-200 text-slate-600 font-medium rounded-xl hover:bg-slate-50 hover:text-slate-900 hover:border-slate-300 shadow-sm flex items-center justify-center gap-2 transition-all"
            >
              <LogOut className="w-4 h-4" />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Layout */}
      <main
        className={`flex-1 min-h-screen transition-all duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)] ${sidebarOpen ? "ml-72" : "ml-0"
          }`}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="fixed top-6 left-6 z-40 p-2.5 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-xl shadow-lg shadow-slate-200/50 hover:bg-white text-slate-600 hover:text-indigo-600 transition-all hover:scale-105 active:scale-95"
          style={{
            left: sidebarOpen ? '19.5rem' : '1.5rem',
            transition: 'left 300ms cubic-bezier(0.25,0.1,0.25,1)'
          }}
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        {hasData ? (
          <div className="max-w-7xl mx-auto px-8 py-12 md:py-16">
            {/* Header */}
            <div className="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="flex items-center gap-3 mb-4">
                <span className="px-3 py-1 bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-bold rounded-full shadow-sm uppercase tracking-wide">
                  {lessonData?.level}
                </span>
                <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full flex items-center gap-1">
                  {LANGUAGE_FLAGS[lessonData?.language || language]} {languages.find(l => l.code === (lessonData?.language || language))?.name}
                </span>
                <span className="text-slate-400 text-sm font-medium flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                  {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </span>
              </div>
              <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
                {lessonData?.topic || "Custom Lesson"}
              </h1>
            </div>

            {/* Navigation Tabs */}
            <div className="flex gap-2 mb-8 p-1 bg-slate-100/50 rounded-2xl w-fit border border-slate-200/50 backdrop-blur-sm">
              {navItems.map(({ key, label, icon: Icon, count }) => (
                <button
                  key={key}
                  onClick={() => setActiveView(key as any)}
                  className={`px-5 py-2.5 text-sm font-medium rounded-xl transition-all flex items-center gap-2.5 ${activeView === key
                    ? "bg-white text-indigo-700 shadow-md shadow-slate-200 ring-1 ring-black/5"
                    : "text-slate-500 hover:text-slate-900 hover:bg-slate-200/50"
                    }`}
                >
                  <Icon className={`w-4 h-4 ${activeView === key ? "text-indigo-600" : "text-slate-400"}`} />
                  {label}
                  {count !== undefined && count > 0 && (
                    <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${activeView === key ? "bg-indigo-50 text-indigo-700" : "bg-slate-200 text-slate-600"
                      }`}>
                      {count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Content Views */}
            <div className="min-h-[600px] animate-in fade-in duration-500">
              {activeView === "objectives" && (
                htmlContent ? (
                  <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden ring-1 ring-black/[0.02]">
                    <iframe
                      srcDoc={htmlContent.replace('</body>', '<script>switchTab("lesson-plan");</script></body>')}
                      className="w-full h-[850px] border-none"
                      title="Lesson Objectives"
                    />
                  </div>
                ) : (
                  <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {lessonData?.vocabulary && lessonData.vocabulary.length > 0 && (
                      <div className="space-y-4">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                          <BookOpen className="w-5 h-5 text-indigo-600" />
                          Key Vocabulary
                        </h2>
                        <VocabularyList vocabulary={lessonData.vocabulary} language={lessonData.language || language} />
                      </div>
                    )}

                    {lessonData?.grammar && lessonData.grammar.length > 0 && (
                      <div className="space-y-4">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                          <Sparkles className="w-5 h-5 text-amber-500" />
                          Grammar Points
                        </h2>
                        <div className="grid gap-4">
                          {lessonData.grammar.map((point: any, idx: number) => (
                            <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-shadow">
                              <div className="flex items-start gap-3">
                                <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded-md text-xs font-bold uppercase tracking-wide flex-shrink-0 mt-1">
                                  Point {idx + 1}
                                </span>
                                <h3 className="font-bold text-lg text-slate-800">{point.structure || point.point}</h3>
                              </div>
                              <p className="mt-2 text-slate-600 leading-relaxed text-sm">{point.explanation}</p>
                              {point.examples && point.examples.length > 0 && (
                                <div className="mt-4 bg-slate-50 p-4 rounded-lg">
                                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Examples</p>
                                  <ul className="space-y-2">
                                    {point.examples.map((ex: string, i: number) => (
                                      <li key={i} className="text-sm text-slate-700 italic flex items-start gap-2">
                                        <span className="text-amber-400 mt-1">•</span>
                                        {ex}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              )}

              {activeView === "reading" && (
                htmlContent ? (
                  <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden ring-1 ring-black/[0.02]">
                    <iframe
                      srcDoc={htmlContent.replace('</body>', '<script>switchTab("story");</script></body>')}
                      className="w-full h-[850px] border-none"
                      title="Reading"
                    />
                  </div>
                ) : (
                  <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm animate-in fade-in zoom-in-95 duration-500">
                    <div className="prose prose-slate max-w-none prose-headings:font-serif prose-p:text-slate-600 prose-p:leading-relaxed">
                      <div className="mb-6 pb-6 border-b border-slate-100 flex items-center justify-between">
                        <h2 className="text-2xl font-bold text-slate-800 font-serif">Reading Passage</h2>
                        <span className="text-sm text-slate-400 italic">Read carefully and answer questions</span>
                      </div>
                      <div className="whitespace-pre-wrap font-serif text-lg text-slate-700 leading-loose">
                        {lessonData?.story || "No reading content available."}
                      </div>
                    </div>
                  </div>
                )
              )}



              {activeView === "quiz" && lessonData && (
                <Quiz
                  questions={lessonData.quiz}
                  story={lessonData.story}
                  language={lessonData.language || language}
                  apiBaseUrl={apiBaseUrl}
                  authApiUrl={authApiUrl}
                  lessonFilename={lessonData.filename}
                />
              )}

              {activeView === "writing" && (
                <WritingExercise
                  key={(lessonData?.topic || topic) + (lessonData?.level || level)}
                  topic={lessonData?.topic || topic}
                  level={lessonData?.level || level}
                  language={lessonData?.language || language}
                  apiBaseUrl={apiBaseUrl}
                  authApiUrl={authApiUrl}
                  initialPrompt={lessonData?.writing_prompt}
                  lessonFilename={lessonData?.filename}
                  initialHistory={lessonData?.progress?.writing_history}
                />
              )}
            </div>
          </div>
        ) : (
          /* Empty State / Loading State */
          <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50/50 via-slate-50 to-slate-100">
            <div className="text-center max-w-md px-8 -mt-20">
              <div className={`w-20 h-20 rounded-3xl bg-white shadow-xl shadow-indigo-100 flex items-center justify-center mx-auto mb-8 border border-slate-50 ${loading ? 'animate-bounce' : ''}`}>
                {loading ? <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" /> : <Sparkles className="w-10 h-10 text-indigo-500" />}
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">
                {loading ? "Crafting your lesson..." : "Ready to learn?"}
              </h2>
              <div className="text-slate-500 text-lg leading-relaxed mb-8">
                {loading ? (
                  <div className="flex flex-col gap-3 mt-6 w-full max-w-xs mx-auto text-left">
                    {[
                      "Planning lesson structure...",
                      "Writing reading passage...",
                      "Analyzing vocabulary & grammar...",
                      "Designing interactive quizzes...",
                      "Finalizing lesson..."
                    ].map((step, index) => (
                      <div key={index} className={`flex items-center gap-3 transition-colors duration-500 ${index === loadingStep ? "text-indigo-600 font-medium" :
                        index < loadingStep ? "text-slate-400" : "text-slate-300"
                        }`}>
                        {index < loadingStep ? (
                          <Check className="w-5 h-5 text-emerald-500" />
                        ) : index === loadingStep ? (
                          <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
                        ) : (
                          <Circle className="w-5 h-5" />
                        )}
                        <span className="text-sm">{step}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <>Choose a language and topic in the sidebar to generate a personalized lesson.</>
                )}
              </div>
              {!loading && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="px-6 py-3 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl shadow-sm hover:shadow-md hover:border-indigo-200 hover:text-indigo-600 transition-all text-sm"
                >
                  Open Sidebar to Start
                </button>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Floating Chat */}
      {lessonData && (
        <RoleplayChat
          lessonContext={lessonData.story || ""}
          characterName="Teacher"
          language={lessonData.language || language}
        />
      )}
      <PricingModal isOpen={showPricing} onClose={() => setShowPricing(false)} />
    </div>
  );
}
