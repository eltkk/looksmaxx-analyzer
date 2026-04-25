import io
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from typing import Optional

from metrics import compute_metrics
from gemini import get_analysis

mp_face_mesh = mp.solutions.face_mesh


def _load_image(contents: bytes) -> tuple[np.ndarray, int, int]:
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img_np = np.array(img)
    return img_np, img_np.shape[1], img_np.shape[0]


def _get_ethnicity_age(img_np: np.ndarray) -> tuple[str, int]:
    try:
        from deepface import DeepFace
        result = DeepFace.analyze(
            img_np,
            actions=["race", "age"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(result, list):
            result = result[0]
        ethnicity = result.get("dominant_race", "unknown")
        age = result.get("age", 0)
        return ethnicity, int(age)
    except Exception:
        return "unknown", 0


def analyze_face(
    contents: bytes,
    height: Optional[str] = None,
    weight: Optional[str] = None,
    nationality: Optional[str] = None,
) -> dict:
    img_np, img_w, img_h = _load_image(contents)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        raise ValueError("Лицо не найдено на фото. Загрузи чёткое фото лица анфас.")

    landmarks = results.multi_face_landmarks[0].landmark
    metrics = compute_metrics(landmarks, img_w, img_h)

    ethnicity, age = _get_ethnicity_age(img_np)

    analysis = get_analysis(metrics, height, weight, nationality, ethnicity, age)

    # Build response
    metrics_display = analysis.get("metrics_display", {})
    return {
        "overall_tier": analysis.get("overall_tier", "MTN"),
        "overall_score": float(analysis.get("overall_score", 5.0)),
        "summary": analysis.get("summary", ""),
        "face_parts": analysis.get("face_parts", []),
        "general_advice": analysis.get("general_advice", []),
        "metrics": {
            "symmetry": metrics.get("symmetry", 0),
            "facial_thirds": metrics_display.get("facial_thirds", metrics.get("facial_thirds", "")),
            "canthal_tilt": metrics_display.get("canthal_tilt", f"{metrics.get('canthal_tilt', 0)}°"),
            "jaw_width": metrics_display.get("jaw_width", str(metrics.get("jaw_width_ratio", ""))),
        },
    }
