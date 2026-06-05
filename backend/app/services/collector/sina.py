import httpx
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional
from app.services.collector.base import BaseCollector

logger = logging.getLogger(__name__)

# 新浪备用采集器的浏览器请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

MAX_RETRIES = 3
RETRY_DELAY = 0.5


class SinaCollector(BaseCollector):
    """新浪财经备用数据采集器"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            http2=False,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )

    async def _request_with_retry(self, url: str, params: dict = None) -> Optional[httpx.Response]:
        """带重试的 HTTP 请求"""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = await self.client.get(url, params=params)
                if resp.status_code == 200:
                    return resp
                logger.warning(f"新浪返回非200状态码: {resp.status_code}, 尝试 {attempt + 1}/{MAX_RETRIES}")
            except httpx.RemoteProtocolError as e:
                last_error = e
                logger.warning(f"新浪连接断开(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except httpx.ConnectTimeout as e:
                last_error = e
                logger.warning(f"新浪连接超时(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except httpx.ReadTimeout as e:
                last_error = e
                logger.warning(f"新浪读取超时(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            except Exception as e:
                last_error = e
                logger.warning(f"新浪请求异常(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")

            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))

        logger.error(f"新浪请求失败，已重试 {MAX_RETRIES} 次: {last_error}")
        return None

    async def fetch_quote(self, symbol: str) -> Optional[dict]:
        prefix = self._get_market_prefix(symbol)
        code = f"{prefix}{symbol}"
        resp = await self._request_with_retry(f"https://hq.sinajs.cn/list={code}")
        if resp is None:
            return None
        try:
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
            logger.warning(f"新浪解析 {symbol} 行情数据失败: {e}")
            return None

    async def fetch_quote_list(self, page: int = 1, page_size: int = 20,
                               sort_by: str = "change_pct", sort_order: str = "desc",
                               market: str = "all") -> Optional[dict]:
        """使用新浪行情中心 API 获取行情列表（备用）"""
        # 新浪行情中心 API - 支持 A 股列表
        sort_map = {
            "change_pct": "changepercent",
            "volume": "volume",
            "amount": "amount",
            "turnover": "turnoverratio",
        }
        sort_field = sort_map.get(sort_by, "changepercent")
        sort_dir = 0 if sort_order == "desc" else 1

        page_num = page - 1  # 新浪从 0 开始
        market_type = 1 if market == "sh" else (2 if market == "sz" else 0)

        resp = await self._request_with_retry(
            "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
            params={
                "page": page_num,
                "num": page_size,
                "sort": sort_field,
                "asc": sort_dir,
                "node": f"hs_a{market_type}" if market_type else "hs_a",
                "symbol": "",
                "_s_r_a": "auto",
            }
        )
        if resp is None:
            return None
        try:
            result = resp.json()
            if not result:
                return None

            items = []
            for row in result:
                items.append({
                    "symbol": row.get("code", "").replace("sh", "").replace("sz", ""),
                    "name": row.get("name", ""),
                    "price": float(row.get("trade", 0) or 0),
                    "change_pct": float(row.get("changepercent", 0) or 0),
                    "change": float(row.get("pricechange", 0) or 0),
                    "volume": int(float(row.get("volume", 0) or 0)),
                    "amount": float(row.get("amount", 0) or 0),
                    "amplitude": 0,
                    "turnover_rate": float(row.get("turnoverratio", 0) or 0),
                    "high": float(row.get("high", 0) or 0),
                    "low": float(row.get("low", 0) or 0),
                    "open": float(row.get("open", 0) or 0),
                    "prev_close": float(row.get("settlement", 0) or 0),
                })

            return {
                "items": items,
                "total": 5000,  # 新浪不返回总数，给一个估算值
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.warning(f"新浪解析行情列表数据失败: {e}")
            return None

    async def fetch_kline(self, symbol: str, period: str = "d",
                          fq_type: str = "front", limit: int = 120) -> Optional[dict]:
        """使用新浪 K 线 API"""
        prefix = self._get_market_prefix(symbol)
        code = f"{prefix}{symbol}"

        # 新浪 K 线周期映射
        period_map = {"1m": "5", "5m": "5", "15m": "15", "30m": "30", "60m": "60", "d": "day", "w": "week", "m": "month"}
        kline_type = period_map.get(period, "day")

        resp = await self._request_with_retry(
            "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20KLineService.getKLineData",
            params={
                "symbol": code,
                "scale": kline_type,
                "ma": "no",
                "datalen": limit,
            }
        )
        if resp is None:
            return None
        try:
            # 新浪返回 JSONP 格式，需要提取 JSON 部分
            text = resp.text
            if "(" in text and ")" in text:
                json_str = text[text.index("(") + 1:text.rindex(")")]
            else:
                json_str = text
            result = json.loads(json_str) if isinstance(json_str, str) else json_str

            if not result:
                return None

            items = []
            for row in result:
                items.append({
                    "date": row.get("day", ""),
                    "open": float(row.get("open", 0)),
                    "close": float(row.get("close", 0)),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "volume": int(float(row.get("volume", 0))),
                    "amount": 0,
                    "change_pct": 0,
                })

            return {
                "symbol": symbol,
                "period": period,
                "fq_type": fq_type,
                "items": items,
            }
        except Exception as e:
            logger.warning(f"新浪解析 {symbol} K线数据失败: {e}")
            return None

    async def fetch_timeline(self, symbol: str) -> Optional[dict]:
        """使用新浪分时 API"""
        prefix = self._get_market_prefix(symbol)
        code = f"{prefix}{symbol}"

        resp = await self._request_with_retry(
            f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20TLineService.getTLineData",
            params={"symbol": code}
        )
        if resp is None:
            return None
        try:
            text = resp.text
            if "(" in text and ")" in text:
                json_str = text[text.index("(") + 1:text.rindex(")")]
            else:
                json_str = text
            result = json.loads(json_str) if isinstance(json_str, str) else json_str

            data = result if isinstance(result, dict) else {}
            if not data:
                return None

            prev_close = float(data.get("prev_close", 0) or 0)
            points = []
            for row in data.get("data", []):
                points.append({
                    "time": row.get("time", ""),
                    "price": float(row.get("price", 0)),
                    "avg": float(row.get("avg_price", 0)),
                    "volume": int(float(row.get("volume", 0))),
                })

            return {
                "symbol": symbol,
                "date": datetime.now().strftime("%Y%m%d"),
                "prev_close": prev_close,
                "points": points,
            }
        except Exception as e:
            logger.warning(f"新浪解析 {symbol} 分时数据失败: {e}")
            return None

    async def fetch_orderbook(self, symbol: str) -> Optional[dict]:
        """使用新浪盘口 API"""
        prefix = self._get_market_prefix(symbol)
        code = f"{prefix}{symbol}"

        resp = await self._request_with_retry(f"https://hq.sinajs.cn/list={code}")
        if resp is None:
            return None
        try:
            text = resp.text
            if '=""' in text:
                return None
            parts = text.split('"')[1].split(",")
            if len(parts) < 32:
                return None

            asks = [
                {"level": 5, "price": float(parts[27]) if parts[27] else 0, "volume": int(float(parts[28])) if parts[28] else 0},
                {"level": 4, "price": float(parts[23]) if parts[23] else 0, "volume": int(float(parts[24])) if parts[24] else 0},
                {"level": 3, "price": float(parts[19]) if parts[19] else 0, "volume": int(float(parts[20])) if parts[20] else 0},
                {"level": 2, "price": float(parts[15]) if parts[15] else 0, "volume": int(float(parts[16])) if parts[16] else 0},
                {"level": 1, "price": float(parts[11]) if parts[11] else 0, "volume": int(float(parts[12])) if parts[12] else 0},
            ]
            bids = [
                {"level": 1, "price": float(parts[9]) if parts[9] else 0, "volume": int(float(parts[10])) if parts[10] else 0},
                {"level": 2, "price": float(parts[7]) if parts[7] else 0, "volume": int(float(parts[8])) if parts[8] else 0},
                {"level": 3, "price": float(parts[5]) if parts[5] else 0, "volume": int(float(parts[6])) if parts[6] else 0},
                {"level": 4, "price": float(parts[3]) if parts[3] else 0, "volume": int(float(parts[4])) if parts[4] else 0},
                {"level": 5, "price": float(parts[1]) if parts[1] else 0, "volume": int(float(parts[2])) if parts[2] else 0},
            ]

            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "asks": asks,
                "bids": bids,
            }
        except Exception as e:
            logger.warning(f"新浪解析 {symbol} 盘口数据失败: {e}")
            return None
