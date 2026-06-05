from fastapi import APIRouter, Query
from app.services.collector.eastmoney import EastMoneyCollector

router = APIRouter(prefix="/stock", tags=["股票基础"])

# 简单的股票搜索（使用东方财富建议接口）
_search_client = EastMoneyCollector()


@router.get("/search")
async def search_stock(keyword: str = Query(..., description="搜索关键词"), limit: int = Query(10, ge=1, le=20)):
    """搜索股票（支持代码和拼音首字母）"""
    import httpx
    items = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://searchapi.eastmoney.com/api/suggest/get", params={
                "input": keyword,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": limit,
            })
            data = resp.json()
            for item in data.get("QuotationCodeTable", {}).get("Data", []):
                code = item.get("Code", "")
                # 只返回A股
                mkt = item.get("MktNum", "")
                if mkt in ("0", "1") and (code.startswith(("0", "3", "6"))):
                    items.append({
                        "symbol": code,
                        "name": item.get("Name", ""),
                        "market": "sh" if code.startswith("6") else "sz",
                        "pinyin": item.get("Pingyin", ""),
                    })
    except Exception:
        pass
    return {"code": 0, "message": "success", "data": {"items": items}}