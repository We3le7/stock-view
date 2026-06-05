from fastapi import APIRouter, Query
from app.ai.interface import create_ai_adapter
from app.core.config import get_settings

router = APIRouter(prefix="/ai", tags=["AI 分析"])

settings = get_settings()


@router.post("/analyze")
async def ai_analyze(symbol: str = Query(...), analysis_type: str = "comprehensive", period_days: int = 30):
    """请求 AI 分析"""
    adapter = create_ai_adapter(settings.AI_ADAPTER)
    result = await adapter.analyze(symbol, analysis_type, period_days)
    return {"code": 0, "message": "success", "data": result}


@router.get("/history")
async def ai_history(symbol: str = Query(None), page: int = Query(1), page_size: int = Query(20)):
    """获取 AI 分析历史（预留）"""
    return {"code": 0, "message": "success", "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}


@router.get("/model-info")
async def ai_model_info():
    """获取 AI 模型信息"""
    adapter = create_ai_adapter(settings.AI_ADAPTER)
    info = adapter.get_model_info()
    return {"code": 0, "message": "success", "data": info}