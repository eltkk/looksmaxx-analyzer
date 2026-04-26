# FaceRank — AI Face Analysis

Web app that analyzes facial geometry using computer vision and scores facial features against looksmaxxing metrics.

**Live:** [perceptive-insight-production-be1a.up.railway.app](https://perceptive-insight-production-be1a.up.railway.app)

---

## What it does

Upload a photo → get a detailed breakdown of 8 facial zones with scores, tier rating, and improvement advice.

The analysis pipeline:
1. **MediaPipe Face Mesh** detects 468 facial landmarks
2. Computes geometric metrics (canthal tilt, facial thirds, jaw/cheekbone ratio, symmetry, FWHR, IPD, etc.)
3. **DeepFace** estimates age and ethnicity
4. Rule-based scoring engine compares each metric against ideal anthropometric ranges
5. Returns tier rating (SUB3 → ADAM), per-zone scores, and personalized advice

No external AI API calls — everything runs on-server.

---

## Tech stack

**Frontend**
- Next.js 16 (App Router) + React 19
- TypeScript
- Tailwind CSS v4
- Lucide icons

**Backend**
- FastAPI + Uvicorn
- MediaPipe 0.10 — face landmark detection
- OpenCV + Pillow — image processing
- DeepFace — age/ethnicity estimation
- In-memory result store with TTL

**Infrastructure**
- Docker (multi-stage builds for both services)
- Railway (separate frontend + backend deployments)

---

## Architecture

```
Browser
  │
  ├── GET  /                    Next.js — landing + upload form
  ├── POST /api/analyze         Next.js API route → proxies to backend
  └── GET  /results/[id]        Next.js — results page
                                      │
                              FastAPI backend
                                      │
                              POST /analyze
                                ├── MediaPipe (landmarks)
                                ├── compute_metrics()
                                ├── DeepFace (age/race)
                                └── scoring engine → store → return id

                              GET /results/{id}
                                └── in-memory store → return result
```

---

## Local development

```bash
# Clone
git clone https://github.com/eltkk/looksmaxx-analyzer
cd looksmaxx-analyzer

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
BACKEND_URL=http://localhost:8000 npm run dev
```

Or with Docker Compose:

```bash
docker compose up
```

App runs at `http://localhost:3000`.

---

## Project structure

```
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Landing + upload form
│   │   ├── results/[id]/         # Results page
│   │   └── api/
│   │       ├── analyze/          # Proxy to backend
│   │       └── results/[id]/     # Proxy to backend
│   └── Dockerfile
│
└── backend/
    ├── main.py                   # FastAPI routes
    ├── analyzer.py               # Analysis orchestration
    ├── metrics.py                # MediaPipe landmark → metric computation
    ├── gemini.py                 # Scoring engine
    ├── storage.py                # In-memory result store (TTL 1h)
    └── Dockerfile
```

---

## Key metrics computed

| Metric | Description |
|--------|-------------|
| Canthal tilt | Angle of eye corners — positive (hunter eyes) vs negative |
| Symmetry | Left/right distance comparison across 4 landmark pairs |
| Facial thirds | Upper / mid / lower face proportion (ideal 33/33/33) |
| Jaw-to-face ratio | Jaw width relative to face width |
| FWHR | Face width-to-height ratio |
| Nose ratio | Alar base width relative to face width |
| Mouth-to-nose ratio | Mouth width / nose width |
| IPD ratio | Inter-pupillary distance / face width |

---

## Deployment

Each service deploys independently on Railway from the same GitHub repo using `railway.toml` per service.

Frontend requires `BACKEND_URL` env var pointing to the backend service URL.
