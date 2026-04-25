import os
import uuid
import asyncio
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from analyzer import analyze_face
from storage import store_result, get_result

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(
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
        raise HTTPException(status_code=500, detail="Ошибка анализа. Попробуй другое фото.")

    result["id"] = result_id
    if height:
        result["height"] = int(height)
    if weight:
        result["weight"] = int(weight)
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
