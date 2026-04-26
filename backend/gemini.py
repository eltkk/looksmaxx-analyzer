from typing import Optional


def _score_metric(value: float, ideal_min: float, ideal_max: float) -> float:
    if ideal_min <= value <= ideal_max:
        return 9.0
    ideal_mid = (ideal_min + ideal_max) / 2
    deviation = abs(value - ideal_mid) / ideal_mid
    return max(1.0, 9.0 - deviation * 18)


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
        return ("Кантальный тилт выраженно позитивный — внешние уголки глаз заметно подняты вверх. Это один из наиболее желанных признаков охотничьего взгляда, который считается маскулинным и привлекательным.",
                "Поддерживай низкий процент жира — это подчёркивает орбитальные кости.")
    if tilt >= 1:
        return ("Кантальный тилт слабо позитивный — уголки глаз немного приподняты. Это нейтрально-хорошая черта, взгляд выглядит бодро и молодо.",
                "Упражнения на мимику и правильная осанка головы помогают подчеркнуть тилт.")
    if tilt >= -1:
        return ("Кантальный тилт нейтральный — уголки глаз на одном уровне. Взгляд нейтральный, не создаёт ни охотничьего, ни усталого эффекта.",
                "Рассмотри апекс-трейнинг и жевательные упражнения для улучшения периорбитальной зоны.")
    return ("Кантальный тилт негативный — внешние уголки глаз опущены вниз. Это создаёт усталый или грустный вид и снижает общую привлекательность взгляда.",
            "Уменьшение процента жира и работа над осанкой могут визуально скорректировать эту зону.")


def _describe_symmetry(sym: float) -> tuple[str, str]:
    if sym >= 92:
        return ("Симметрия лица исключительно высокая — асимметрия практически незаметна. Это редкая черта, сильно ассоциированная с генетическим здоровьем и привлекательностью.",
                "Поддерживай одностороннее жевание попеременно для сохранения симметрии.")
    if sym >= 85:
        return ("Симметрия лица хорошая — незначительные отклонения в пределах нормы. Большинство людей не замечают асимметрию при первом взгляде.",
                "Сон на спине снижает асимметрию лица в долгосрочной перспективе.")
    if sym >= 75:
        return ("Симметрия лица средняя — асимметрия заметна при детальном рассмотрении. Это распространённая картина и не является критическим недостатком.",
                "Обрати внимание на позу во время сна и жевание — жуй с обеих сторон равномерно.")
    return ("Симметрия лица ниже среднего — асимметрия заметна невооружённым глазом. Это может быть следствием привычек сна, жевания или постуральных паттернов.",
            "Жевательные упражнения с обеих сторон и сон на спине — приоритет номер один.")


def _describe_jaw(ratio: float) -> tuple[str, str]:
    if 0.75 <= ratio <= 0.85:
        return ("Соотношение челюсти к скулам идеальное — хорошо развитая нижняя треть при выраженных скулах. Это создаёт мужественный треугольник лица.",
                "Жевание твёрдой пищи и мьюинг поддерживают развитие этой зоны.")
    if ratio < 0.75:
        return ("Челюсть заметно уже скул — нижняя треть лица слабее выражена. Это создаёт более мягкий профиль лица.",
                "Мьюинг, жевание твёрдой пищи (вяленое мясо, орехи) и снижение жира развивают нижнюю челюсть.")
    return ("Челюсть широкая относительно скул — нижняя треть доминирует. В умеренной степени это маскулинная черта.",
            "Снижение процента жира подчеркнёт скуловую зону и улучшит соотношение.")


def _describe_nose(ratio: float) -> tuple[str, str]:
    if 0.20 <= ratio <= 0.25:
        return ("Ширина носа в идеальном соотношении с лицом — нос пропорционален и гармонично вписывается в черты лица.",
                "Ринопластика не требуется — эта зона является сильной стороной.")
    if ratio < 0.20:
        return ("Нос узкий относительно ширины лица — это создаёт утончённый вид. В западных стандартах считается привлекательным.",
                "Контуринг переносицы с помощью причёски или оправы очков подчёркивает эту черту.")
    return ("Нос широкий относительно ширины лица — превышает оптимальный диапазон пропорций.",
            "Снижение жира немного сужает носовую область. Причёска и оправы очков могут визуально скорректировать.")


def _describe_lips(ratio: float) -> tuple[str, str]:
    if 1.4 <= ratio <= 1.6:
        return ("Соотношение губ к носу идеальное — губы пропорционально соответствуют нижней зоне лица. Это один из классических признаков гармоничных черт.",
                "Поддерживай нормальный вес — это сохраняет объём губ.")
    if ratio < 1.4:
        return ("Губы узкие относительно носа — нижняя треть выглядит несколько сжатой.",
                "Гидратация и правильный мьюинг (давление языка на нёбо) постепенно улучшают эту область.")
    return ("Губы широкие относительно носа — выходят за пределы оптимального диапазона.",
            "Причёска и щетина могут скорректировать визуальное восприятие нижней трети.")


def _describe_eyes(ratio: float) -> tuple[str, str]:
    if 0.28 <= ratio <= 0.35:
        return ("Пропорции глаз оптимальные — соотношение высоты к ширине в идеальном диапазоне. Это создаёт выразительный, миндалевидный разрез глаз.",
                "Поддерживай низкий процент жира для сохранения чёткости орбитальной зоны.")
    if ratio < 0.28:
        return ("Глаза узкие — горизонтальный разрез доминирует над вертикальным. Это создаёт более закрытый взгляд.",
                "Уменьшение процента жира открывает глаза. Правильный сон снижает отёчность.")
    return ("Глаза крупные — вертикальный размер выражен. В определённых стандартах это привлекательная черта.",
            "Тренировка периорбитальных мышц поддерживает тонус этой зоны.")


def _describe_forehead(thirds: str) -> tuple[str, str]:
    try:
        parts = [float(x.strip()) for x in thirds.split("/")]
        top = parts[0]
    except Exception:
        top = 33.0
    if 30 <= top <= 36:
        return ("Лоб пропорционально вписывается в верхнюю треть лица — гармоничное распределение черт.",
                "Причёска может подчеркнуть или скорректировать визуальный размер лба.")
    if top < 30:
        return ("Лоб небольшой — верхняя треть лица укорочена. Это создаёт компактный вид.",
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
    canthal = metrics.get("canthal_tilt", 0)
    symmetry = metrics.get("symmetry", 0)
    jaw = metrics.get("jaw_width_ratio", 0)
    nose = metrics.get("nose_ratio", 0)
    mouth = metrics.get("mouth_to_nose_ratio", 0)
    eye = metrics.get("eye_ratio", 0)
    fwhr = metrics.get("fwhr", 0)
    ipd = metrics.get("ipd_ratio", 0)
    thirds = metrics.get("facial_thirds", "33/33/33")

    eye_score = round((_score_metric(eye, 0.28, 0.35) + _score_metric(canthal, 1, 5) + _score_metric(ipd, 0.42, 0.50)) / 3, 1)
    nose_score = round(_score_metric(nose, 0.20, 0.25), 1)
    jaw_score = round((_score_metric(jaw, 0.75, 0.85) + _score_metric(fwhr, 1.8, 2.1)) / 2, 1)
    cheek_score = round(_score_metric(jaw, 0.68, 0.78), 1)
    lip_score = round(_score_metric(mouth, 1.4, 1.6), 1)
    sym_score = round(symmetry / 10, 1)
    brow_score = round(_score_metric(canthal, 0, 5), 1)
    forehead_score = 7.0

    overall = round((eye_score * 1.5 + nose_score + jaw_score * 1.3 + cheek_score * 1.2 + lip_score + sym_score * 1.4 + brow_score + forehead_score) / 9.4, 1)
    overall = min(9.9, max(1.0, overall))
    tier = _score_to_tier(overall)

    eye_desc, eye_advice = _describe_eyes(eye)
    nose_desc, nose_advice = _describe_nose(nose)
    jaw_desc, jaw_advice = _describe_jaw(jaw)
    lip_desc, lip_advice = _describe_lips(mouth)
    sym_desc, sym_advice = _describe_symmetry(symmetry)
    cant_desc, cant_advice = _describe_canthal(canthal)
    fore_desc, fore_advice = _describe_forehead(thirds)

    height_txt = f"{height} см" if height else "не указан"
    weight_txt = f"{weight} кг" if weight else "не указан"
    nat_txt = nationality or ethnicity or "не указана"

    if overall >= 8.5:
        summary = f"Выдающиеся черты лица — тир {tier}. Пропорции лица близки к эталонным стандартам лусмаксинга. Генетика на высоком уровне, потенциал для максимизации внешности очень высок."
    elif overall >= 7.0:
        summary = f"Сильные черты лица — тир {tier}. Большинство пропорций в хорошем диапазоне, есть отдельные зоны для улучшения. При правильном подходе к лусмаксингу возможен существенный прогресс."
    elif overall >= 5.5:
        summary = f"Средние черты лица — тир {tier}. Пропорции в норме, но далеки от эталона. Есть конкретные точки роста, работа над которыми даст заметный результат."
    else:
        summary = f"Черты лица ниже среднего — тир {tier}. Значительный потенциал для улучшения через лусмаксинг-протоколы. Системная работа над каждой зоной даст результат."

    if height and weight:
        try:
            h, w = float(height) / 100, float(weight)
            bmi = w / (h * h)
            if bmi > 25:
                summary += f" Снижение веса (сейчас ИМТ ~{bmi:.1f}) значительно улучшит черты лица."
        except Exception:
            pass

    canthal_display = f"+{canthal:.1f}°" if canthal >= 0 else f"{canthal:.1f}°"
    status = "позитивный" if canthal >= 1 else ("нейтральный" if canthal >= -1 else "негативный")

    return {
        "overall_tier": tier,
        "overall_score": overall,
        "summary": summary,
        "metrics_display": {
            "symmetry": round(symmetry),
            "facial_thirds": thirds,
            "canthal_tilt": f"{canthal_display} ({status})",
            "jaw_width": f"{'Идеальная' if 0.75 <= jaw <= 0.85 else ('Узкая' if jaw < 0.75 else 'Широкая')} ({jaw:.2f})",
        },
        "face_parts": [
            {"name": "Глаза", "score": eye_score, "rating": _score_to_tier(eye_score), "description": eye_desc, "advice": eye_advice},
            {"name": "Нос", "score": nose_score, "rating": _score_to_tier(nose_score), "description": nose_desc, "advice": nose_advice},
            {"name": "Челюсть и подбородок", "score": jaw_score, "rating": _score_to_tier(jaw_score), "description": jaw_desc, "advice": jaw_advice},
            {"name": "Скулы", "score": cheek_score, "rating": _score_to_tier(cheek_score), "description": "Скуловая зона определяет верхнюю ширину лица и создаёт характерный треугольник привлекательности.", "advice": "Снижение процента жира — главный инструмент для выраженности скул."},
            {"name": "Брови", "score": brow_score, "rating": _score_to_tier(brow_score), "description": cant_desc, "advice": cant_advice},
            {"name": "Губы", "score": lip_score, "rating": _score_to_tier(lip_score), "description": lip_desc, "advice": lip_advice},
            {"name": "Лоб", "score": forehead_score, "rating": _score_to_tier(forehead_score), "description": fore_desc, "advice": fore_advice},
            {"name": "Симметрия", "score": sym_score, "rating": _score_to_tier(sym_score), "description": sym_desc, "advice": sym_advice},
        ],
        "general_advice": [
            "Снизь процент жира до 10-12% — это главный лусмаксинг-инструмент, раскрывающий все черты лица.",
            "Практикуй мьюинг ежедневно — правильное положение языка на нёбе развивает средний отдел лица.",
            "Жуй твёрдую пищу (вяленое мясо, орехи) — это развивает массетеры и нижнюю треть лица.",
            "Спи на спине без подушки — предотвращает асимметрию и сохраняет черты лица.",
            "Работай над осанкой (forward head posture убирает до 2 баллов у любого лица).",
        ],
    }
