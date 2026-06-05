import httpx
import logging
from datetime import datetime
from typing import Optional
from app.services.collector.base import BaseCollector

logger = logging.getLogger(__name__)


class SinaCollector(BaseCollector):
    """新浪财经备用数据采集器"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": "https://finance.sina.com.cn/",
        })

    async def fetch_quote(self, symbol: str) -> Optional[dict]:
        prefix = self._get_market_prefix(symbol)
        code = f"{prefix}{symbol}"
        try:
            resp = await self.client.get(f"https://hq.sinajs.cn/list={code}")
            text = resp.text
            if '=""' in text:
                return None
            parts = text.split('"')[1].split(",")
            if len(parts) < 32:
                return None
            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0
            prev_close = float(parts[2]) if parts[2] else 0
            price = float(parts[3]) if parts[3] else 0
            high = float(parts[4]) if parts[4] else 0
            low = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[8])) if parts[8] else 0
            amount = float(parts[9]) if parts[9] else 0

            change = round(price - prev_close, 3) if prev_close else 0
            change_pct = round(change / prev_close * 100, 2) if prev_close else 0

            return {
                "symbol": symbol,
                "name": name,
                "market": prefix,
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "open": open_price,
                "high": high,
                "low": low,
                "prev_close": prev_close,
                "volume": volume,
                "amount": amount,
                "turnover_rate": 0.0,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            }
        except Exception as e:
            logger.warning(f"新浪获取 {symbol} 行情失败: {e}")
            return None

    async def fetch_quote_list(self, page: int = 1, page_size: int = 20,
                               sort_by: str = "change_pct", sort_order: str = "desc",
                               market: str = "all") -> Optional[dict]:
        logger.warning("新浪财经不支持行情列表接口，请使用东方财富")
        return None

    async def fetch_kline(self, symbol: str, period: str = "d",
                          fq_type: str = "front", limit: int = 120) -> Optional[dict]:
        logger.warning("新浪财经 K 线接口暂未实现，请使用东方财富")
        return None

    async def fetch_timeline(self, symbol: str) -> Optional[dict]:
        logger.warning("新浪财经分时接口暂未实现，请使用东方财富")
        return None

    async def fetch_orderbook(self, symbol: str) -> Optional[dict]:
        logger.warning("新浪财经盘口接口暂未实现，请使用东方财富")
        return None