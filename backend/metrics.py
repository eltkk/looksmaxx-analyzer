import math
import numpy as np
from typing import Any


def _pt(lm: Any, idx: int, w: int, h: int) -> tuple[float, float]:
    p = lm[idx]
    return p.x * w, p.y * h


def _dist(a: tuple, b: tuple) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def compute_metrics(landmarks, img_w: int, img_h: int) -> dict:
    lm = landmarks

    # Key points
    left_eye_inner  = _pt(lm, 133, img_w, img_h)
    left_eye_outer  = _pt(lm, 33,  img_w, img_h)
    right_eye_inner = _pt(lm, 362, img_w, img_h)
    right_eye_outer = _pt(lm, 263, img_w, img_h)
    left_eye_top    = _pt(lm, 159, img_w, img_h)
    left_eye_bot    = _pt(lm, 145, img_w, img_h)
    right_eye_top   = _pt(lm, 386, img_w, img_h)
    right_eye_bot   = _pt(lm, 374, img_w, img_h)

    nose_tip   = _pt(lm, 4,   img_w, img_h)
    nose_base  = _pt(lm, 94,  img_w, img_h)
    nose_left  = _pt(lm, 129, img_w, img_h)
    nose_right = _pt(lm, 358, img_w, img_h)

    mouth_left  = _pt(lm, 61,  img_w, img_h)
    mouth_right = _pt(lm, 291, img_w, img_h)
    mouth_top   = _pt(lm, 13,  img_w, img_h)
    mouth_bot   = _pt(lm, 14,  img_w, img_h)

    chin        = _pt(lm, 152, img_w, img_h)
    forehead    = _pt(lm, 10,  img_w, img_h)
    jaw_left    = _pt(lm, 234, img_w, img_h)
    jaw_right   = _pt(lm, 454, img_w, img_h)
    cheek_left  = _pt(lm, 116, img_w, img_h)
    cheek_right = _pt(lm, 345, img_w, img_h)

    brow_left_inner  = _pt(lm, 107, img_w, img_h)
    brow_left_outer  = _pt(lm, 70,  img_w, img_h)
    brow_right_inner = _pt(lm, 336, img_w, img_h)
    brow_right_outer = _pt(lm, 300, img_w, img_h)
    brow_left_top    = _pt(lm, 105, img_w, img_h)
    brow_right_top   = _pt(lm, 334, img_w, img_h)

    # Canthal tilt (angle of eye corners)
    dx = right_eye_inner[0] - left_eye_inner[0]
    dy = right_eye_inner[1] - left_eye_inner[1]
    canthal_angle = math.degrees(math.atan2(-dy, dx))

    # Eye dimensions
    eye_width_l = _dist(left_eye_outer, left_eye_inner)
    eye_width_r = _dist(right_eye_outer, right_eye_inner)
    eye_height_l = _dist(left_eye_top, left_eye_bot)
    eye_height_r = _dist(right_eye_top, right_eye_bot)
    eye_width_avg = (eye_width_l + eye_width_r) / 2
    eye_height_avg = (eye_height_l + eye_height_r) / 2
    eye_ratio = eye_height_avg / eye_width_avg if eye_width_avg > 0 else 0

    # Interpupillary distance
    ipd = _dist(
        ((left_eye_inner[0] + left_eye_outer[0]) / 2, (left_eye_inner[1] + left_eye_outer[1]) / 2),
        ((right_eye_inner[0] + right_eye_outer[0]) / 2, (right_eye_inner[1] + right_eye_outer[1]) / 2),
    )

    # Face width (bizygomatic)
    face_width = _dist(cheek_left, cheek_right)

    # Facial thirds
    face_height = _dist(forehead, chin)
    upper_third = abs(forehead[1] - ((left_eye_top[1] + right_eye_top[1]) / 2))
    mid_third   = abs(((left_eye_top[1] + right_eye_top[1]) / 2) - nose_base[1])
    lower_third = abs(nose_base[1] - chin[1])

    thirds_ratio = f"{upper_third/face_height*100:.0f} / {mid_third/face_height*100:.0f} / {lower_third/face_height*100:.0f}"

    # Jaw width
    jaw_width = _dist(jaw_left, jaw_right)
    jaw_to_cheek = jaw_width / face_width if face_width > 0 else 0

    # Nose dimensions
    nose_width = _dist(nose_left, nose_right)
    nose_length = _dist(nose_base, nose_tip)
    nose_ratio = nose_width / face_width if face_width > 0 else 0

    # Mouth width
    mouth_width = _dist(mouth_left, mouth_right)
    mouth_height = _dist(mouth_top, mouth_bot)
    mouth_to_nose = mouth_width / nose_width if nose_width > 0 else 0
    mouth_width_ratio = mouth_width / face_width if face_width > 0 else 0

    # Brow dimensions
    brow_width_l = _dist(brow_left_outer, brow_left_inner)
    brow_width_r = _dist(brow_right_outer, brow_right_inner)
    brow_width_avg = (brow_width_l + brow_width_r) / 2
    brow_height_l = abs(brow_left_top[1] - left_eye_top[1])
    brow_height_r = abs(brow_right_top[1] - right_eye_top[1])
    brow_arch = (brow_height_l + brow_height_r) / 2
    brow_width_ratio = brow_width_avg / face_width if face_width > 0 else 0

    # Symmetry — compare left vs right half distances
    sym_points = [
        (_dist(left_eye_outer, nose_tip), _dist(right_eye_outer, nose_tip)),
        (_dist(jaw_left, chin), _dist(jaw_right, chin)),
        (_dist(mouth_left, nose_tip), _dist(mouth_right, nose_tip)),
        (_dist(cheek_left, nose_tip), _dist(cheek_right, nose_tip)),
    ]
    sym_scores = []
    for l, r in sym_points:
        if max(l, r) > 0:
            sym_scores.append(1 - abs(l - r) / max(l, r))
    symmetry = round(sum(sym_scores) / len(sym_scores) * 100, 1) if sym_scores else 50.0

    # Face width-to-height ratio
    fwhr = face_width / face_height if face_height > 0 else 0

    return {
        "canthal_tilt": round(canthal_angle, 2),
        "facial_thirds": thirds_ratio,
        "jaw_width_ratio": round(jaw_to_cheek, 3),
        "nose_ratio": round(nose_ratio, 3),
        "mouth_to_nose_ratio": round(mouth_to_nose, 3),
        "mouth_width_ratio": round(mouth_width_ratio, 3),
        "eye_ratio": round(eye_ratio, 3),
        "brow_arch_mm": round(brow_arch, 1),
        "brow_width_ratio": round(brow_width_ratio, 3),
        "fwhr": round(fwhr, 3),
        "symmetry": symmetry,
        "ipd_ratio": round(ipd / face_width, 3) if face_width > 0 else 0,
        "face_width_px": round(face_width, 1),
        "face_height_px": round(face_height, 1),
        "mouth_width_px": round(mouth_width, 1),
        "nose_width_px": round(nose_width, 1),
        "jaw_width_px": round(jaw_width, 1),
        "eye_width_avg_px": round(eye_width_avg, 1),
        "brow_width_avg_px": round(brow_width_avg, 1),
    }
