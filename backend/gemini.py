from typing import Optional


def _score_canthal(tilt: float) -> float:
    if tilt >= 4:   return 9.5
    if tilt >= 2:   return 8.0
    if tilt >= 0.5: return 6.5
    if tilt >= -1:  return 5.0
    if tilt >= -3:  return 3.5
    return 2.0


def _score_symmetry(sym: float) -> float:
    # MediaPipe symmetry skews high — recalibrate
    if sym >= 96:  return 9.0
    if sym >= 92:  return 7.5
    if sym >= 86:  return 6.0
    if sym >= 78:  return 4.5
    if sym >= 68:  return 3.0
    return 2.0


def _score_range(value: float, ideal_min: float, ideal_max: float, floor: float = 2.0) -> float:
    if ideal_min <= value <= ideal_max:
        return 8.2
    span = ideal_max - ideal_min
    distance = max(0, ideal_min - value, value - ideal_max)
    penalty = (distance / span) * 12.0
    return max(floor, 8.2 - penalty)


def _score_to_tier(score: float) -> str:
    if score >= 9.5: return "ADAM"
    if score >= 8.5: return "TRUE CHAD"
    if score >= 7.0: return "CHAD"
    if score >= 6.0: return "HTN"
    if score >= 5.0: return "MTN"
    if score >= 4.0: return "LTN"
    if score >= 3.0: return "SUB5"
    return "SUB3"


def _describe_canthal(tilt: float) -> tuple[str, str]:
    if tilt >= 3:
        return ("Кантальный тилт выраженно позитивный — внешние уголки глаз заметно подняты. Это один из наиболее желанных признаков охотничьего взгляда, маскулинного и привлекательного.",
                "Поддерживай низкий процент жира — это подчёркивает орбитальные кости и усиливает тилт.")
    if tilt >= 1:
        return ("Кантальный тилт слабо позитивный — уголки глаз немного приподняты. Взгляд выглядит бодро и молодо.",
                "Жевательные упражнения и мьюинг развивают скуловую зону, что со временем влияет на кантальный тилт.")
    if tilt >= -1:
        return ("Кантальный тилт нейтральный — уголки глаз на одном уровне. Не создаёт ни охотничьего, ни усталого эффекта.",
                "Апекс-трейнинг и снижение жира в лице могут улучшить визуальное восприятие взгляда.")
    if tilt >= -3:
        return ("Кантальный тилт негативный — внешние уголки немного опущены. Создаёт слегка усталый вид.",
                "Снижение процента жира и работа над осанкой — ключевые инструменты для улучшения этой зоны.")
    return ("Кантальный тилт выраженно негативный — внешние уголки глаз опущены вниз. Это создаёт усталый вид и снижает привлекательность взгляда.",
            "Снижение жира в лице и правильная осанка — приоритет. Ринопластика периорбитальной зоны — хирургический вариант.")


def _describe_symmetry(sym: float) -> tuple[str, str]:
    if sym >= 92:
        return ("Симметрия лица исключительно высокая — асимметрия практически незаметна. Редкая черта, сильно ассоциированная с генетическим здоровьем.",
                "Поддерживай одностороннее жевание попеременно для сохранения симметрии.")
    if sym >= 82:
        return ("Симметрия лица хорошая — незначительные отклонения в пределах нормы. Большинство людей не замечают асимметрию при первом взгляде.",
                "Сон на спине снижает асимметрию лица в долгосрочной перспективе.")
    if sym >= 70:
        return ("Симметрия лица средняя — асимметрия заметна при детальном рассмотрении.",
                "Жуй с обеих сторон равномерно, спи на спине.")
    return ("Симметрия лица ниже среднего — асимметрия заметна невооружённым глазом.",
            "Жевательные упражнения с обеих сторон и сон на спине — приоритет номер один.")


def _describe_jaw(ratio: float) -> tuple[str, str]:
    # jaw_to_cheek: landmarks 234/454 vs 116/345 — ratio ~0.95-1.20 is normal
    if 0.95 <= ratio <= 1.10:
        return ("Соотношение ширины лица в норме — пропорциональная нижняя треть. Создаёт сбалансированный профиль лица.",
                "Жевание твёрдой пищи и мьюинг поддерживают развитие этой зоны.")
    if ratio < 0.95:
        return ("Нижняя треть лица немного уже — лицо имеет сужающийся к подбородку профиль.",
                "Жевание твёрдой пищи (вяленое мясо, орехи) и мьюинг развивают нижнюю челюсть.")
    return ("Нижняя треть лица широкая — хорошо развитая челюсть. В умеренной степени это маскулинная черта.",
            "Снижение процента жира подчеркнёт угол челюсти и улучшит визуальное соотношение.")


def _describe_nose(ratio: float) -> tuple[str, str]:
    # nose_ratio = nose_width / face_width, ideal 0.27-0.33
    if 0.27 <= ratio <= 0.33:
        return ("Ширина носа пропорциональна ширине лица — нос гармонично вписывается в черты.",
                "Эта зона является сильной стороной — ринопластика не требуется.")
    if ratio < 0.27:
        return ("Нос узкий относительно ширины лица — утончённый вид, привлекательный в большинстве стандартов.",
                "Причёска и оправа очков могут дополнительно подчеркнуть эту черту.")
    return ("Нос широкий относительно ширины лица — выходит за пределы оптимального диапазона.",
            "Снижение жира в лице немного сужает носовую область. Контуринг причёской помогает визуально.")


def _describe_lips(ratio: float) -> tuple[str, str]:
    if 1.25 <= ratio <= 1.65:
        return ("Соотношение губ к носу идеальное — губы пропорционально соответствуют нижней зоне лица.",
                "Поддерживай нормальный вес — это сохраняет объём и форму губ.")
    if ratio < 1.25:
        return ("Губы узкие относительно носа — нижняя зона выглядит немного сжатой.",
                "Гидратация и правильный мьюинг постепенно улучшают эту область.")
    return ("Губы широкие относительно носа — нижняя треть лица доминирует по ширине.",
            "Щетина и определённые причёски могут скорректировать визуальное восприятие.")


def _describe_eyes(ratio: float) -> tuple[str, str]:
    # eye_ratio = eye_height / eye_width, typical 0.22-0.40
    if 0.25 <= ratio <= 0.38:
        return ("Пропорции глаз оптимальные — миндалевидный разрез глаз в идеальном диапазоне. Создаёт выразительный, привлекательный взгляд.",
                "Поддерживай низкий процент жира для сохранения чёткости орбитальной зоны.")
    if ratio < 0.25:
        return ("Глаза с более узким вертикальным разрезом — горизонтальный формат. В некоторых стандартах это ассоциируется с охотничьим взглядом.",
                "Снижение жира и правильный сон уменьшают отёчность и открывают глаза.")
    return ("Глаза с выраженным вертикальным открытием — крупный разрез. Привлекательно во многих стандартах красоты.",
            "Тренировка периорбитальных мышц поддерживает тонус этой зоны.")


def _describe_forehead(thirds: str) -> tuple[str, str]:
    try:
        parts = [float(x.strip()) for x in thirds.split("/")]
        top = parts[0]
    except Exception:
        top = 33.0
    if 28 <= top <= 38:
        return ("Лоб пропорционально вписывается в верхнюю треть лица — гармоничное распределение черт.",
                "Причёска может дополнительно подчеркнуть или скорректировать визуальный размер лба.")
    if top < 28:
        return ("Лоб небольшой — верхняя треть лица укорочена.",
                "Причёски с объёмом на макушке визуально увеличивают лоб.")
    return ("Лоб высокий — верхняя треть лица удлинена.",
            "Причёски с чёлкой или горизонтальными линиями визуально уменьшают лоб.")


def get_analysis(
    metrics: dict,
    height: Optional[str],
    weight: Optional[str],
    nationality: Optional[str],
    ethnicity: str,
    age: int,
) -> dict:
    canthal      = metrics.get("canthal_tilt", 0)
    symmetry     = metrics.get("symmetry", 0)
    jaw          = metrics.get("jaw_width_ratio", 0)
    nose         = metrics.get("nose_ratio", 0)
    mouth        = metrics.get("mouth_to_nose_ratio", 0)
    mouth_w      = metrics.get("mouth_width_ratio", 0)
    eye          = metrics.get("eye_ratio", 0)
    fwhr         = metrics.get("fwhr", 0)
    ipd          = metrics.get("ipd_ratio", 0)
    thirds       = metrics.get("facial_thirds", "33/33/33")
    brow_w       = metrics.get("brow_width_ratio", 0)
    face_h       = metrics.get("face_height_px", 1)
    brow_arch_px = metrics.get("brow_arch_mm", 0)
    brow_arch_r  = brow_arch_px / face_h if face_h > 0 else 0

    # Per-zone scores with correct ranges for these MediaPipe landmarks
    cant_s  = round(_score_canthal(canthal), 1)
    eye_s   = round((_score_range(eye, 0.25, 0.38) + cant_s + _score_range(ipd, 0.38, 0.52)) / 3, 1)
    nose_s  = round(_score_range(nose, 0.27, 0.33), 1)
    jaw_s   = round((_score_range(jaw, 0.95, 1.12) + _score_range(fwhr, 0.60, 0.80)) / 2, 1)
    cheek_s = round(_score_range(fwhr, 0.62, 0.78), 1)
    lip_s   = round(_score_range(mouth, 1.25, 1.65), 1)
    sym_s   = round(_score_symmetry(symmetry), 1)
    brow_s  = round((_score_range(brow_w, 0.15, 0.28) + cant_s) / 2, 1)
    fore_s  = round(_score_range(float(thirds.split("/")[0]) if "/" in thirds else 33, 28, 38), 1)

    overall = round(
        (eye_s * 1.4 + nose_s + jaw_s * 1.3 + cheek_s * 1.1 + lip_s + sym_s * 1.2 + brow_s + fore_s) / 10.0,
        1
    )
    overall = min(9.9, max(2.0, overall))
    tier = _score_to_tier(overall)

    eye_desc, eye_adv   = _describe_eyes(eye)
    nose_desc, nose_adv = _describe_nose(nose)
    jaw_desc, jaw_adv   = _describe_jaw(jaw)
    lip_desc, lip_adv   = _describe_lips(mouth)
    sym_desc, sym_adv   = _describe_symmetry(symmetry)
    cant_desc, cant_adv = _describe_canthal(canthal)
    fore_desc, fore_adv = _describe_forehead(thirds)

    if overall >= 8.5:
        summary = f"Выдающиеся черты лица — тир {tier}. Пропорции близки к эталонным стандартам лусмаксинга. Высокий генетический потенциал."
    elif overall >= 7.0:
        summary = f"Сильные черты лица — тир {tier}. Большинство пропорций в хорошем диапазоне, есть отдельные зоны для улучшения."
    elif overall >= 5.5:
        summary = f"Средние черты лица — тир {tier}. Пропорции в норме, но есть конкретные точки роста — работа над ними даст заметный результат."
    else:
        summary = f"Черты лица ниже среднего — тир {tier}. Значительный потенциал для улучшения через лусмаксинг-протоколы."

    if height and weight:
        try:
            bmi = float(weight) / (float(height) / 100) ** 2
            if bmi > 25:
                summary += f" Снижение веса (ИМТ ~{bmi:.1f}) заметно улучшит черты лица."
        except Exception:
            pass

    canthal_display = f"+{canthal:.1f}°" if canthal >= 0 else f"{canthal:.1f}°"
    status = "позитивный" if canthal >= 1 else ("нейтральный" if canthal >= -1 else "негативный")
    jaw_label = "Норма" if 0.95 <= jaw <= 1.15 else ("Узкая" if jaw < 0.95 else "Широкая")

    return {
        "overall_tier": tier,
        "overall_score": overall,
        "summary": summary,
        "metrics_display": {
            "symmetry": round(symmetry),
            "facial_thirds": thirds,
            "canthal_tilt": f"{canthal_display} ({status})",
            "jaw_width": f"{jaw_label} ({jaw:.2f})",
        },
        "face_parts": [
            {"name": "Глаза",               "score": eye_s,  "rating": _score_to_tier(eye_s),  "description": eye_desc,  "advice": eye_adv},
            {"name": "Нос",                  "score": nose_s, "rating": _score_to_tier(nose_s), "description": nose_desc, "advice": nose_adv},
            {"name": "Челюсть и подбородок", "score": jaw_s,  "rating": _score_to_tier(jaw_s),  "description": jaw_desc,  "advice": jaw_adv},
            {"name": "Скулы",                "score": cheek_s,"rating": _score_to_tier(cheek_s),"description": "Скуловая зона определяет верхнюю ширину лица и создаёт треугольник привлекательности.", "advice": "Снижение процента жира — главный инструмент для выраженности скул."},
            {"name": "Брови",                "score": brow_s, "rating": _score_to_tier(brow_s), "description": cant_desc + " Оценка учитывает форму и арку — густота бровей по геометрии лица не определяется.", "advice": cant_adv},
            {"name": "Губы",                 "score": lip_s,  "rating": _score_to_tier(lip_s),  "description": lip_desc,  "advice": lip_adv},
            {"name": "Лоб",                  "score": fore_s, "rating": _score_to_tier(fore_s), "description": fore_desc, "advice": fore_adv},
            {"name": "Симметрия",            "score": sym_s,  "rating": _score_to_tier(sym_s),  "description": sym_desc,  "advice": sym_adv},
        ],
        "general_advice": [
            "Снизь процент жира до 10-12% — это главный лусмаксинг-инструмент, раскрывающий все черты лица.",
            "Практикуй мьюинг ежедневно — правильное положение языка на нёбе развивает средний отдел лица.",
            "Жуй твёрдую пищу (вяленое мясо, орехи) — это развивает массетеры и нижнюю треть лица.",
            "Спи на спине без подушки — предотвращает асимметрию и сохраняет черты лица.",
            "Работай над осанкой — forward head posture визуально ухудшает черты лица у любого человека.",
        ],
    }
