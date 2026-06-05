from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db
from app.core.redis import close_redis
from app.api.v1 import quote, stock, watchlist, ai
from app.api.websocket import router as ws_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    await init_db()
    yield
    # 关闭
    await close_redis()


app = FastAPI(
    title="Stock-View API",
    description="A股实时行情查看与AI分析平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(quote.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}