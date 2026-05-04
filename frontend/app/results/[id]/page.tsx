"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Scan, ArrowLeft, ChevronDown, ChevronUp, Lightbulb, Trophy,
  Share2, Check, Eye, Crosshair, Hexagon, Diamond, Minus, Smile,
  ArrowUp, Sliders, type LucideIcon,
} from "lucide-react";

interface FacePart {
  name: string;
  score: number;
  rating: string;
  description: string;
  advice: string;
}

interface AnalysisResult {
  id: string;
  overall_tier: string;
  overall_score: number;
  summary: string;
  face_parts: FacePart[];
  general_advice: string[];
  metrics: {
    symmetry: number;
    facial_thirds: string;
    canthal_tilt: string;
    jaw_width: string;
  };
  height?: number;
  weight?: number;
  nationality?: string;
  photo_url?: string;
}

const TIER_COLORS: Record<string, string> = {
  ADAM: "text-yellow-300",
  "TRUE CHAD": "text-yellow-300",
  CHAD: "text-yellow-400",
  HTN: "text-green-400",
  MTN: "text-blue-400",
  LTN: "text-orange-400",
  SUB5: "text-red-400",
  SUB3: "text-red-600",
};

const TIER_BG: Record<string, string> = {
  ADAM: "bg-yellow-300/10 border-yellow-300/30",
  "TRUE CHAD": "bg-yellow-300/10 border-yellow-300/30",
  CHAD: "bg-yellow-400/10 border-yellow-400/30",
  HTN: "bg-green-400/10 border-green-400/30",
  MTN: "bg-blue-400/10 border-blue-400/30",
  LTN: "bg-orange-400/10 border-orange-400/30",
  SUB5: "bg-red-400/10 border-red-400/30",
  SUB3: "bg-red-600/10 border-red-600/30",
};

const SCORE_COLOR = (score: number) => {
  if (score >= 8) return "text-yellow-400";
  if (score >= 6.5) return "text-green-400";
  if (score >= 5) return "text-blue-400";
  if (score >= 3.5) return "text-orange-400";
  return "text-red-400";
};

const SCORE_BAR = (score: number) => {
  if (score >= 8) return "bg-yellow-400";
  if (score >= 6.5) return "bg-green-400";
  if (score >= 5) return "bg-blue-400";
  if (score >= 3.5) return "bg-orange-400";
  return "bg-red-400";
};

const ZONE_ICONS: Record<string, LucideIcon> = {
  "Глаза": Eye,
  "Нос": Crosshair,
  "Челюсть и подбородок": Hexagon,
  "Скулы": Diamond,
  "Брови": Minus,
  "Губы": Smile,
  "Лоб": ArrowUp,
  "Симметрия": Sliders,
};

function FacePartCard({ part, index }: { part: FacePart; index: number }) {
  const [open, setOpen] = useState(false);
  const Icon = ZONE_ICONS[part.name] ?? Scan;

  return (
    <div
      className="glass rounded-2xl overflow-hidden animate-fade-in-up"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center flex-shrink-0">
            <Icon className={`w-4 h-4 ${SCORE_COLOR(part.score)}`} />
          </div>
          <div className="text-left">
            <div className="text-white font-semibold">{part.name}</div>
            <div className={`text-sm font-bold ${SCORE_COLOR(part.score)}`}>{part.rating}</div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className={`text-2xl font-bold ${SCORE_COLOR(part.score)}`}>
              {part.score.toFixed(1)}
            </div>
            <div className="text-zinc-600 text-xs">/ 10</div>
          </div>
          <div className="w-24 h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${SCORE_BAR(part.score)}`}
              style={{ width: `${(part.score / 10) * 100}%` }}
            />
          </div>
          {open ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
        </div>
      </button>

      {open && (
        <div className="px-6 pb-5 border-t border-white/5 pt-4 space-y-3">
          <p className="text-zinc-300 text-sm leading-relaxed">{part.description}</p>
          <div className="flex items-start gap-2 bg-purple-500/10 border border-purple-500/20 rounded-xl p-3">
            <Lightbulb className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
            <p className="text-purple-200 text-sm leading-relaxed">{part.advice}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [displayScore, setDisplayScore] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const photo = sessionStorage.getItem("facerank_photo");
    if (photo) {
      setPhotoPreview(photo);
      sessionStorage.removeItem("facerank_photo");
    }
  }, []);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await fetch(`/api/results/${params.id}`);
        if (!res.ok) throw new Error("Результат не найден");
        const data = await res.json();
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    };

    if (params.id) fetchResult();
  }, [params.id]);

  useEffect(() => {
    if (!result) return;
    const target = result.overall_score;
    const duration = 1200;
    const fps = 60;
    const steps = duration / (1000 / fps);
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      setDisplayScore(parseFloat(current.toFixed(1)));
      if (current >= target) clearInterval(timer);
    }, 1000 / fps);
    return () => clearInterval(timer);
  }, [result]);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-zinc-400">Анализируем лицо...</p>
          <p className="text-zinc-600 text-sm mt-1">Обычно занимает 10-20 секунд</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-xl transition-colors"
          >
            На главную
          </button>
        </div>
      </div>
    );
  }

  const tierColor = TIER_COLORS[result.overall_tier] ?? "text-zinc-400";
  const tierBg = TIER_BG[result.overall_tier] ?? "bg-zinc-800/50 border-zinc-700";

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Nav */}
      <nav className="border-b border-white/5 px-6 py-4 flex items-center justify-between sticky top-0 bg-[#09090b]/90 backdrop-blur-sm z-10">
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-purple-600 flex items-center justify-center">
            <Scan className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-bold text-white tracking-tight">FaceRank</span>
        </div>
        <button
          onClick={handleShare}
          className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors text-sm"
        >
          {copied ? <Check className="w-4 h-4 text-green-400" /> : <Share2 className="w-4 h-4" />}
          <span className={copied ? "text-green-400" : ""}>{copied ? "Скопировано" : "Поделиться"}</span>
        </button>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-12 space-y-8">
        {/* Overall Result */}
        <div className={`rounded-3xl border p-8 text-center ${tierBg} animate-fade-in-up`}>
          {photoPreview && (
            <div className="flex justify-center mb-5">
              <img
                src={photoPreview}
                alt="Твоё фото"
                className="w-20 h-20 rounded-full object-cover border-2 border-white/10"
              />
            </div>
          )}
          <div className="flex items-center justify-center gap-2 text-zinc-500 text-sm mb-4">
            <Trophy className="w-4 h-4" />
            Итоговый тир
          </div>
          <div className={`text-7xl font-black mb-3 ${tierColor}`}>
            {result.overall_tier}
          </div>
          <div className="flex items-center justify-center gap-3 mb-6">
            <span className={`text-4xl font-bold tabular-nums ${SCORE_COLOR(result.overall_score)}`}>
              {displayScore.toFixed(1)}
            </span>
            <span className="text-zinc-600 text-xl">/ 10</span>
          </div>
          <p className="text-zinc-300 leading-relaxed max-w-lg mx-auto">{result.summary}</p>

          {(result.height || result.weight || result.nationality) && (
            <div className="flex items-center justify-center gap-4 mt-6 text-sm text-zinc-500">
              {result.height && <span>{result.height} см</span>}
              {result.weight && <span>{result.weight} кг</span>}
              {result.nationality && <span>{result.nationality}</span>}
            </div>
          )}
        </div>

        {/* Metrics */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-white font-bold mb-4 text-lg">Метрики лица</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Симметрия", value: `${result.metrics.symmetry}%` },
              { label: "Трети лица", value: result.metrics.facial_thirds },
              { label: "Кантальный тилт", value: result.metrics.canthal_tilt },
              { label: "Ширина челюсти", value: result.metrics.jaw_width },
            ].map(({ label, value }) => (
              <div key={label} className="bg-zinc-900 rounded-xl p-4">
                <div className="text-zinc-500 text-xs mb-1">{label}</div>
                <div className="text-white font-semibold">{value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Face Parts */}
        <div>
          <h2 className="text-white font-bold mb-4 text-lg">Анализ по зонам</h2>
          <div className="space-y-3">
            {result.face_parts.map((part, i) => (
              <FacePartCard key={part.name} part={part} index={i} />
            ))}
          </div>
        </div>

        {/* General Advice */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-white font-bold mb-4 text-lg flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-purple-400" />
            Общие рекомендации
          </h2>
          <ul className="space-y-3">
            {result.general_advice.map((advice, i) => (
              <li key={i} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-purple-400 text-xs font-bold">{i + 1}</span>
                </div>
                <p className="text-zinc-300 text-sm leading-relaxed">{advice}</p>
              </li>
            ))}
          </ul>
        </div>

        {/* CTA */}
        <div className="text-center pb-8">
          <button
            onClick={() => router.push("/")}
            className="bg-purple-600 hover:bg-purple-500 text-white px-8 py-4 rounded-xl font-semibold transition-all duration-200 flex items-center gap-2 mx-auto"
          >
            <Scan className="w-5 h-5" />
            Новый анализ
          </button>
        </div>
      </div>
    </div>
  );
}
