"use client";

import { useEffect, useState } from "react";
import { Scan } from "lucide-react";

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

export default function AnalyzingPage() {
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 2000);

    const progressInterval = setInterval(() => {
      setProgress((p) => (p < 95 ? p + 1 : p));
    }, 170);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col items-center justify-center px-6">
      {/* Scanner */}
      <div className="relative w-48 h-48 mb-12">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full border border-purple-500/20" />
        <div className="absolute inset-2 rounded-full border border-purple-500/30" />
        <div className="absolute inset-4 rounded-full border border-purple-500/40" />

        {/* Spinning arc */}
        <svg className="absolute inset-0 w-full h-full animate-spin" style={{ animationDuration: "2s" }}>
          <circle
            cx="96" cy="96" r="88"
            fill="none"
            stroke="url(#grad)"
            strokeWidth="2"
            strokeDasharray="120 440"
            strokeLinecap="round"
          />
          <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Reverse spinning arc */}
        <svg className="absolute inset-0 w-full h-full animate-spin" style={{ animationDuration: "3s", animationDirection: "reverse" }}>
          <circle
            cx="96" cy="96" r="70"
            fill="none"
            stroke="url(#grad2)"
            strokeWidth="1"
            strokeDasharray="60 380"
            strokeLinecap="round"
          />
          <defs>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="1" />
            </linearGradient>
          </defs>
        </svg>

        {/* Center icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-20 h-20 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <Scan className="w-9 h-9 text-purple-400" />
          </div>
        </div>

        {/* Corner markers */}
        {[
          "top-0 left-0 border-t-2 border-l-2 rounded-tl-lg",
          "top-0 right-0 border-t-2 border-r-2 rounded-tr-lg",
          "bottom-0 left-0 border-b-2 border-l-2 rounded-bl-lg",
          "bottom-0 right-0 border-b-2 border-r-2 rounded-br-lg",
        ].map((cls, i) => (
          <div key={i} className={`absolute w-5 h-5 border-purple-500 ${cls}`} />
        ))}
      </div>

      {/* Status text */}
      <div className="text-center mb-8">
        <h2 className="text-white text-xl font-semibold mb-2">Анализируем лицо</h2>
        <p className="text-purple-400 text-sm min-h-[20px] transition-all duration-500">
          {STEPS[step]}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-64">
        <div className="flex justify-between text-xs text-zinc-600 mb-2">
          <span>Прогресс</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-600 to-indigo-500 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
