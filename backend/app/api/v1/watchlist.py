from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db
from app.models.models import Watchlist as WatchlistModel
from app.schemas.schemas import WatchlistAddRequest, WatchlistSortRequest

router = APIRouter(prefix="/watchlist", tags=["自选股"])

DEFAULT_USER_ID = 1


@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    """获取自选股列表"""
    result = await db.execute(
        select(WatchlistModel).where(WatchlistModel.user_id == DEFAULT_USER_ID).order_by(WatchlistModel.sort_order)
    )
    items = result.scalars().all()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [{"symbol": w.symbol, "name": "", "market": w.market, "sort_order": w.sort_order} for w in items]
        },
    }


@router.post("")
async def add_watchlist(req: WatchlistAddRequest, db: AsyncSession = Depends(get_db)):
    """添加自选股"""
    existing = await db.execute(
        select(WatchlistModel).where(
            WatchlistModel.user_id == DEFAULT_USER_ID,
            WatchlistModel.symbol == req.symbol,
        )
    )
    if existing.scalar_one_or_none():
        return {"code": 1001, "message": "已在自选股中", "data": None}

    # 获取最大排序号
    result = await db.execute(
        select(WatchlistModel).where(WatchlistModel.user_id == DEFAULT_USER_ID).order_by(WatchlistModel.sort_order.desc()).limit(1)
    )
    last = result.scalar_one_or_none()
    sort_order = (last.sort_order + 1) if last else 1

    item = WatchlistModel(user_id=DEFAULT_USER_ID, symbol=req.symbol, market=req.market, sort_order=sort_order)
    db.add(item)
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.delete("/{symbol}")
async def remove_watchlist(symbol: str, db: AsyncSession = Depends(get_db)):
    """删除自选股"""
    await db.execute(
        delete(WatchlistModel).where(WatchlistModel.user_id == DEFAULT_USER_ID, WatchlistModel.symbol == symbol)
    )
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.put("/sort")
async def sort_watchlist(req: WatchlistSortRequest, db: AsyncSession = Depends(get_db)):
    """调整自选股排序"""
    for item in req.items:
        result = await db.execute(
            select(WatchlistModel).where(
                WatchlistModel.user_id == DEFAULT_USER_ID, WatchlistModel.symbol == item.symbol
            )
        )
        w = result.scalar_one_or_none()
        if w:
            w.sort_order = item.sort_order
    await db.commit()
    return {"code": 0, "message": "success", "data": None}