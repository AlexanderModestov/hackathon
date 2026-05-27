import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

from apify_client import fetch_trending_reels
from claude_client import generate_script

app = FastAPI()


class GenerateRequest(BaseModel):
    hashtag: str
    creator_topic: str


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        reels = fetch_trending_reels(request.hashtag)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Сервис временно недоступен, попробуй снова")
    except Exception:
        raise HTTPException(status_code=502, detail="Ошибка получения данных")

    if not reels:
        raise HTTPException(status_code=400, detail="Хэштег не найден или нет Reels")

    try:
        result = generate_script(reels, request.creator_topic)
    except Exception:
        raise HTTPException(status_code=502, detail="Ошибка генерации, попробуй снова")

    return result
