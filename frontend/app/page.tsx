"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload, Scan, ChevronRight, Zap, Shield, AlertCircle, RefreshCw, Info } from "lucide-react";

const RATING_EXAMPLES = [
  { tier: "ADAM", color: "text-yellow-300", desc: "Топ 0.1% — легендарный" },
  { tier: "CHAD", color: "text-yellow-400", desc: "Топ 5% — высокий тир" },
  { tier: "HTN", color: "text-green-400", desc: "Выше среднего" },
  { tier: "MTN", color: "text-blue-400", desc: "Средний тир" },
  { tier: "LTN", color: "text-orange-400", desc: "Ниже среднего" },
  { tier: "SUB5", color: "text-red-400", desc: "Нижний тир" },
];

const STEPS = [
  "Определяем лицо на фото...",
  "Анализируем симметрию лица...",
  "Измеряем кантальный тилт...",
  "Оцениваем пропорции трётей...",
  "Анализируем челюсть и скулы...",
  "Изучаем черты лица...",
  "Рассчитываем итоговый тир...",
  "Формируем рекомендации...",
];

export default function HomePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analyzeStep, setAnalyzeStep] = useState(0);
  const [analyzeProgress, setAnalyzeProgress] = useState(0);
  const [analyzeError, setAnalyzeError] = useState("");

  useEffect(() => {
    if (!loading) return;
    setAnalyzeStep(0);
    setAnalyzeProgress(0);
    setAnalyzeError("");

    const stepInterval = setInterval(() => {
      setAnalyzeStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 2000);

    const progressInterval = setInterval(() => {
      setAnalyzeProgress((p) => (p < 90 ? p + 1 : p));
    }, 170);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, [loading]);

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Загрузи изображение (JPG, PNG, WEBP)");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("Файл слишком большой. Максимум 10MB");
      return;
    }
    setError("");
    setPhoto(file);
    const reader = new FileReader();
    reader.onload = (e) => setPhotoPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback(() => setIsDragging(false), []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!photo) {
      setError("Загрузи фото");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("photo", photo);
      if (height) formData.append("height", height);
      if (weight) formData.append("weight", weight);

      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || data.error || "Ошибка анализа");
      }

      if (photoPreview) {
        sessionStorage.setItem("facerank_photo", photoPreview);
      }

      setAnalyzeProgress(100);
      await new Promise((r) => setTimeout(r, 400));
      router.push(`/results/${data.id}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Что-то пошло не так. Попробуй другое фото.";
      setAnalyzeError(msg);
    }
  };

  const handleRetry = () => {
    setLoading(false);
    setAnalyzeError("");
    setAnalyzeProgress(0);
    setAnalyzeStep(0);
  };

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Analyzing overlay */}
      {loading && (
        <div className="fixed inset-0 bg-[#09090b] z-50 flex flex-col items-center justify-center px-6">
          {analyzeError ? (
            <>
              <div className="w-20 h-20 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mb-6">
                <AlertCircle className="w-10 h-10 text-red-400" />
              </div>
              <h2 className="text-white text-xl font-semibold mb-3">Ошибка анализа</h2>
              <p className="text-red-400 text-sm mb-8 max-w-sm text-center leading-relaxed">{analyzeError}</p>
              <button
                onClick={handleRetry}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Попробовать снова
              </button>
            </>
          ) : (
            <>
              <div className="relative w-48 h-48 mb-12">
                <div className="absolute inset-0 rounded-full border border-purple-500/20" />
                <div className="absolute inset-2 rounded-full border border-purple-500/30" />
                <div className="absolute inset-4 rounded-full border border-purple-500/40" />
                <svg className="absolute inset-0 w-full h-full animate-spin" style={{ animationDuration: "2s" }}>
                  <circle cx="96" cy="96" r="88" fill="none" stroke="url(#grad)" strokeWidth="2" strokeDasharray="120 440" strokeLinecap="round" />
                  <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#a855f7" stopOpacity="0" />
                      <stop offset="100%" stopColor="#a855f7" stopOpacity="1" />
                    </linearGradient>
                  </defs>
                </svg>
                <svg className="absolute inset-0 w-full h-full animate-spin" style={{ animationDuration: "3s", animationDirection: "reverse" }}>
                  <circle cx="96" cy="96" r="70" fill="none" stroke="url(#grad2)" strokeWidth="1" strokeDasharray="60 380" strokeLinecap="round" />
                  <defs>
                    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity="0" />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity="1" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
                    <Scan className="w-9 h-9 text-purple-400" />
                  </div>
                </div>
                {["top-0 left-0 border-t-2 border-l-2 rounded-tl-lg", "top-0 right-0 border-t-2 border-r-2 rounded-tr-lg", "bottom-0 left-0 border-b-2 border-l-2 rounded-bl-lg", "bottom-0 right-0 border-b-2 border-r-2 rounded-br-lg"].map((cls, i) => (
                  <div key={i} className={`absolute w-5 h-5 border-purple-500 ${cls}`} />
                ))}
              </div>
              <div className="text-center mb-8">
                <h2 className="text-white text-xl font-semibold mb-2">Анализируем лицо</h2>
                <p className="text-purple-400 text-sm min-h-[20px] transition-all duration-500">
                  {STEPS[analyzeStep]}
                </p>
              </div>
              <div className="w-64">
                <div className="flex justify-between text-xs text-zinc-600 mb-2">
                  <span>Прогресс</span>
                  <span>{analyzeProgress}%</span>
                </div>
                <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-600 to-indigo-500 rounded-full transition-all duration-300"
                    style={{ width: `${analyzeProgress}%` }}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Nav */}
      <nav className="border-b border-white/5 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
            <Scan className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-white text-lg tracking-tight">FaceRank</span>
        </div>
        <div className="text-sm text-zinc-500">Бесплатно</div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 rounded-full px-4 py-1.5 text-sm text-purple-400 mb-6">
          <Zap className="w-3.5 h-3.5" />
          AI анализ лица по системе лусмаксинга
        </div>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Узнай свой{" "}
          <span className="gradient-text">Face Tier</span>
        </h1>
        <p className="text-zinc-400 text-xl max-w-2xl mx-auto leading-relaxed">
          Загрузи фото — ИИ оценит каждую черту лица, определит твой тир и даст
          персональные советы по улучшению
        </p>
      </section>

      {/* Upload Form */}
      <section className="max-w-2xl mx-auto px-6 pb-20">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={[
              "relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-200 overflow-hidden",
              isDragging ? "border-purple-500 bg-purple-500/10" : "border-zinc-700 hover:border-purple-500/50 hover:bg-zinc-900",
              photoPreview ? "border-purple-500/30" : "",
            ].join(" ")}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            {photoPreview ? (
              <div className="relative">
                <img src={photoPreview} alt="Preview" className="w-full max-h-80 object-contain bg-zinc-950" />
                <div className="absolute inset-0 scan-overlay pointer-events-none" />
                <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1.5 text-sm text-purple-400 flex items-center gap-1.5">
                  <Upload className="w-3.5 h-3.5" />
                  Заменить фото
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 px-6">
                <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-4">
                  <Upload className="w-7 h-7 text-purple-400" />
                </div>
                <p className="text-white font-medium mb-1">Загрузи фото лица</p>
                <p className="text-zinc-500 text-sm">Перетащи или нажми сюда · JPG, PNG, WEBP · до 10MB</p>
              </div>
            )}
          </div>

          <div className="flex items-start gap-2 bg-zinc-900/60 border border-zinc-800 rounded-xl px-4 py-3">
            <Info className="w-4 h-4 text-zinc-500 flex-shrink-0 mt-0.5" />
            <p className="text-zinc-500 text-xs leading-relaxed">
              Для точного анализа: смотри прямо в камеру · нейтральное выражение · хорошее освещение · без очков и головных уборов
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-zinc-400 mb-2">Рост (см)</label>
              <input
                type="number"
                placeholder="178"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
                min={140}
                max={220}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-2">Вес (кг)</label>
              <input
                type="number"
                placeholder="75"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                min={40}
                max={200}
                className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !photo}
            className={[
              "w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all duration-200",
              photo && !loading
                ? "bg-purple-600 hover:bg-purple-500 animate-pulse-glow cursor-pointer"
                : "bg-zinc-800 text-zinc-500 cursor-not-allowed",
            ].join(" ")}
          >
            <Scan className="w-5 h-5" />
            Анализировать лицо
            <ChevronRight className="w-4 h-4" />
          </button>

          <p className="text-center text-zinc-600 text-xs">
            Фото не сохраняются · Анализ занимает ~15 секунд
          </p>
        </form>
      </section>

      {/* Rating Scale */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <h2 className="text-center text-2xl font-bold text-white mb-3">Шкала оценок</h2>
        <p className="text-center text-zinc-500 text-sm mb-8">Где ты находишься?</p>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {RATING_EXAMPLES.map((r) => (
            <div key={r.tier} className="glass rounded-xl p-4 text-center">
              <div className={`text-xl font-bold mb-1 ${r.color}`}>{r.tier}</div>
              <div className="text-zinc-500 text-xs">{r.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: Scan, title: "Детальный анализ", desc: "Оценка 8 зон лица: глаза, нос, челюсть, скулы, лоб, подбородок, брови, губы" },
            { icon: Zap, title: "За 15 секунд", desc: "Быстрый ИИ-анализ на основе геометрических пропорций и нейросети" },
            { icon: Shield, title: "Конфиденциально", desc: "Фото анализируются и сразу удаляются. Мы не храним твои данные" },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass rounded-2xl p-6">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-4">
                <Icon className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-zinc-500 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 px-6 py-8 text-center text-zinc-600 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Scan className="w-4 h-4" />
          <span className="font-semibold text-zinc-400">FaceRank</span>
        </div>
        <p>AI-анализ лица · Только для образовательных целей</p>
      </footer>
    </div>
  );
}
