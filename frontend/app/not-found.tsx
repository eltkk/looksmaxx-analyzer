"use client";

import { useRouter } from "next/navigation";
import { Scan } from "lucide-react";

export default function NotFound() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col items-center justify-center px-6 text-center">
      <div className="text-8xl font-black gradient-text mb-4">404</div>
      <h1 className="text-white text-2xl font-bold mb-2">Страница не найдена</h1>
      <p className="text-zinc-500 mb-8">Такой страницы не существует</p>
      <button
        onClick={() => router.push("/")}
        className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-colors"
      >
        <Scan className="w-4 h-4" />
        На главную
      </button>
    </div>
  );
}
