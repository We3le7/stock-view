from fastapi import APIRouter, Query
from app.services.collector.manager import collector_manager

router = APIRouter(prefix="/quote", tags=["行情数据"])


@router.get("/realtime")
async def get_realtime_quote(symbols: str = Query(..., description="股票代码，逗号分隔")):
    """获取实时行情"""
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()][:50]
    items = []
    for symbol in symbol_list:
        data = await collector_manager.fetch_quote(symbol)
        if data:
            items.append(data)
    return {"code": 0, "message": "success", "data": {"items": items}}


@router.get("/list")
async def get_quote_list(
    market: str = Query("all", description="市场: all/sh/sz"),
    sort_by: str = Query("change_pct", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向: asc/desc"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """获取行情列表"""
    data = await collector_manager.fetch_quote_list(
        page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order, market=market
    )
    if data is None:
        return {"code": 1003, "message": "数据源暂不可用", "data": None}
    return {"code": 0, "message": "success", "data": data}


@router.get("/kline")
async def get_kline(
    symbol: str = Query(..., description="股票代码"),
    period: str = Query("d", description="K线周期: 1m/5m/15m/30m/60m/d/w/m"),
    fq_type: str = Query("front", description="复权类型: none/front/back"),
    limit: int = Query(120, ge=1, le=500, description="返回数量"),
):
    """获取 K 线数据"""
    data = await collector_manager.fetch_kline(symbol, period=period, fq_type=fq_type, limit=limit)
    if data is None:
        return {"code": 1002, "message": "股票代码不存在或数据源暂不可用", "data": None}
    return {"code": 0, "message": "success", "data": data}


@router.get("/timeline")
async def get_timeline(symbol: str = Query(..., description="股票代码")):
    """获取分时数据"""
    data = await collector_manager.fetch_timeline(symbol)
    if data is None:
        return {"code": 1002, "message": "股票代码不存在或数据源暂不可用", "data": None}
    return {"code": 0, "message": "success", "data": data}


@router.get("/orderbook")
async def get_orderbook(symbol: str = Query(..., description="股票代码")):
    """获取盘口数据"""
    data = await collector_manager.fetch_orderbook(symbol)
    if data is None:
        return {"code": 1002, "message": "股票代码不存在或数据源暂不可用", "data": None}
    return {"code": 0, "message": "success", "data": data}