from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ========== 通用 ==========
class ResponseBase(BaseModel):
    code: int = 0
    message: str = "success"


# ========== 行情 ==========
class QuoteItem(BaseModel):
    symbol: str
    name: str
    market: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    prev_close: float
    volume: int
    amount: float
    turnover_rate: float = 0.0
    timestamp: str = ""


class QuoteListResponse(ResponseBase):
    data: Optional[dict] = None


class KlineItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float = 0.0
    change_pct: float = 0.0


class KlineResponse(ResponseBase):
    data: Optional[dict] = None


class TimelinePoint(BaseModel):
    time: str
    price: float
    avg: float
    volume: int


class TimelineResponse(ResponseBase):
    data: Optional[dict] = None


class OrderBookLevel(BaseModel):
    level: int
    price: float
    volume: int


class OrderBookResponse(ResponseBase):
    data: Optional[dict] = None


# ========== 股票搜索 ==========
class StockSearchItem(BaseModel):
    symbol: str
    name: str
    market: str
    pinyin: str = ""


# ========== 自选股 ==========
class WatchlistAddRequest(BaseModel):
    symbol: str
    market: str = "sh"


class WatchlistSortItem(BaseModel):
    symbol: str
    sort_order: int


class WatchlistSortRequest(BaseModel):
    items: list[WatchlistSortItem]


# ========== AI 分析 ==========
class AIAnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "comprehensive"
    period_days: int = 30
    include_kline: bool = True
    custom_params: Optional[dict] = None


class AIAnalysisResponse(ResponseBase):
    data: Optional[dict] = None