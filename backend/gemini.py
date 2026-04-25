import os
import json
import httpx
from typing import Optional

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PRIMARY_MODEL   = "google/gemini-2.0-flash-001"
FALLBACK_MODEL  = "google/gemini-2.0-flash-exp:free"

SYSTEM_PROMPT = """Ты эксперт по лусмаксингу и анализу лица. Ты даёшь честные, детальные оценки по реальным метрикам.
Отвечай строго в JSON формате без лишнего текста. Используй только русский язык в описаниях."""

USER_PROMPT_TEMPLATE = """Проанализируй лицо человека по следующим метрикам и дай оценку.

МЕТРИКИ ЛИЦА:
- Кантальный тилт: {canthal_tilt}° (положительный = поднятый внешний уголок глаза)
- Симметрия лица: {symmetry}%
- Пропорции трётей лица: {facial_thirds} (верх/середина/низ, идеал 33/33/33)
- Отношение ширины челюсти к скулам: {jaw_width_ratio} (идеал 0.75-0.85)
- Отношение ширины носа к лицу: {nose_ratio} (идеал 0.20-0.25)
- Отношение рта к носу: {mouth_to_nose_ratio} (идеал 1.4-1.6)
- Отношение высоты к ширине глаза: {eye_ratio} (идеал 0.28-0.35)
- FWHR (ширина/высота лица): {fwhr} (идеал 1.8-2.1)
- IPD к ширине лица: {ipd_ratio} (идеал 0.42-0.50)

ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ:
- Рост: {height}
- Вес: {weight}
- Национальность: {nationality}
- Этничность по DeepFace: {ethnicity}
- Возраст по DeepFace: {age}

ШКАЛА ОЦЕНОК (от худшего к лучшему):
SUB3 → SUB5 → LTN → MTN → HTN → CHAD → TRUE CHAD → ADAM

Верни JSON строго в этом формате:
{{
  "overall_tier": "MTN",
  "overall_score": 5.8,
  "summary": "Краткий итоговый вердикт 2-3 предложения",
  "metrics_display": {{
    "symmetry": 87,
    "facial_thirds": "34 / 33 / 33",
    "canthal_tilt": "+2.1° (позитивный)",
    "jaw_width": "Средняя (0.78)"
  }},
  "face_parts": [
    {{
      "name": "Глаза",
      "score": 6.5,
      "rating": "HTN",
      "description": "Детальное описание черты 2-3 предложения",
      "advice": "Конкретный совет по улучшению"
    }},
    {{
      "name": "Нос",
      "score": 5.0,
      "rating": "MTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Челюсть и подбородок",
      "score": 6.0,
      "rating": "HTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Скулы",
      "score": 5.5,
      "rating": "MTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Брови",
      "score": 5.0,
      "rating": "MTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Губы",
      "score": 5.5,
      "rating": "MTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Лоб",
      "score": 6.0,
      "rating": "HTN",
      "description": "...",
      "advice": "..."
    }},
    {{
      "name": "Симметрия",
      "score": 7.0,
      "rating": "HTN",
      "description": "...",
      "advice": "..."
    }}
  ],
  "general_advice": [
    "Совет 1",
    "Совет 2",
    "Совет 3",
    "Совет 4",
    "Совет 5"
  ]
}}"""


def _call_model(model: str, prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://facerank.app",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def get_analysis(metrics: dict, height: Optional[str], weight: Optional[str], nationality: Optional[str], ethnicity: str, age: int) -> dict:
    prompt = USER_PROMPT_TEMPLATE.format(
        canthal_tilt=metrics.get("canthal_tilt", 0),
        symmetry=metrics.get("symmetry", 0),
        facial_thirds=metrics.get("facial_thirds", "N/A"),
        jaw_width_ratio=metrics.get("jaw_width_ratio", 0),
        nose_ratio=metrics.get("nose_ratio", 0),
        mouth_to_nose_ratio=metrics.get("mouth_to_nose_ratio", 0),
        eye_ratio=metrics.get("eye_ratio", 0),
        fwhr=metrics.get("fwhr", 0),
        ipd_ratio=metrics.get("ipd_ratio", 0),
        height=f"{height} см" if height else "не указан",
        weight=f"{weight} кг" if weight else "не указан",
        nationality=nationality or "не указана",
        ethnicity=ethnicity,
        age=age,
    )

    models = [PRIMARY_MODEL, FALLBACK_MODEL]
    last_err = None

    for model in models:
        try:
            response = _call_model(model, prompt)
            content = response["choices"][0]["message"]["content"].strip()

            # Strip markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            return json.loads(content)
        except (httpx.HTTPStatusError, httpx.TimeoutException) as e:
            last_err = e
            continue
        except json.JSONDecodeError:
            last_err = ValueError("Некорректный JSON от модели")
            continue

    raise RuntimeError(f"Все модели недоступны: {last_err}")
