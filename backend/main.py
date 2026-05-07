import os
import uuid
import asyncio
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from analyzer import analyze_face
from storage import store_result, get_result

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze(
    request: Request,
    photo: UploadFile = File(...),
    height: str = Form(None),
    weight: str = Form(None),
    nationality: str = Form(None),
):
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Нужно изображение")

    contents = await photo.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл слишком большой")

    result_id = str(uuid.uuid4())

    try:
        result = await asyncio.to_thread(
            analyze_face,
            contents,
            height=height,
            weight=weight,
            nationality=nationality,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {type(e).__name__}: {e}")

    result["id"] = result_id
    try:
        if height:
            result["height"] = int(height)
        if weight:
            result["weight"] = int(weight)
    except ValueError:
        pass
    if nationality:
        result["nationality"] = nationality

    store_result(result_id, result)
    return {"id": result_id}


@app.get("/results/{result_id}")
async def get_results(result_id: str):
    result = get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}
