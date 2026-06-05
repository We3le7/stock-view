import httpx
import json
import logging
from datetime import datetime
from typing import Optional
from app.services.collector.base import BaseCollector

logger = logging.getLogger(__name__)


class EastMoneyCollector(BaseCollector):
    """东方财富数据采集器"""

    BASE_URL = "https://push2.eastmoney.com"
    HISTORY_URL = "https://push2his.eastmoney.com"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/",
        })

    async def fetch_quote(self, symbol: str) -> Optional[dict]:
        secid = self._get_secid(symbol)
        try:
            resp = await self.client.get(f"{self.BASE_URL}/api/qt/stock/get", params={
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f116,f117,f162,f168,f169,f170,f171",
                "ut": "fa5fd1943c7b386f172d6893dbfd32",
            })
            data = resp.json().get("data", {})
            if not data:
                return None
            return self._parse_quote(symbol, data)
        except Exception as e:
            logger.warning(f"东方财富获取 {symbol} 行情失败: {e}")
            return None

    async def fetch_quote_list(self, page: int = 1, page_size: int = 20,
                               sort_by: str = "change_pct", sort_order: str = "desc",
                               market: str = "all") -> Optional[dict]:
        sort_field_map = {
            "change_pct": "f3",
            "volume": "f5",
            "amount": "f6",
            "turnover": "f8",
        }
        fid = sort_field_map.get(sort_by, "f3")
        po = 0 if sort_order == "desc" else 1

        fs_map = {
            "all": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "sh": "m:1+t:2,m:1+t:23",
            "sz": "m:0+t:6,m:0+t:80",
        }

        try:
            resp = await self.client.get(f"{self.BASE_URL}/api/qt/clist/get", params={
                "pn": page,
                "pz": page_size,
                "po": po,
                "np": 1,
                "fltt": 2,
                "invt": 2,
                "fid": fid,
                "fs": fs_map.get(market, fs_map["all"]),
                "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18",
            })
            result = resp.json()
            if result.get("data") is None:
                return None

            items = []
            for row in result["data"].get("diff", []):
                items.append({
                    "symbol": row.get("f12", ""),
                    "name": row.get("f14", ""),
                    "price": row.get("f2", 0) or 0,
                    "change_pct": row.get("f3", 0) or 0,
                    "change": row.get("f4", 0) or 0,
                    "volume": row.get("f5", 0) or 0,
                    "amount": row.get("f6", 0) or 0,
                    "amplitude": row.get("f7", 0) or 0,
                    "turnover_rate": row.get("f8", 0) or 0,
                    "high": row.get("f15", 0) or 0,
                    "low": row.get("f16", 0) or 0,
                    "open": row.get("f17", 0) or 0,
                    "prev_close": row.get("f18", 0) or 0,
                })

            return {
                "items": items,
                "total": result["data"].get("total", 0),
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.warning(f"东方财富获取行情列表失败: {e}")
            return None

    async def fetch_kline(self, symbol: str, period: str = "d",
                          fq_type: str = "front", limit: int = 120) -> Optional[dict]:
        secid = self._get_secid(symbol)
        klt_map = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "60m": 60, "d": 101, "w": 102, "m": 103}
        fqt_map = {"none": 0, "front": 1, "back": 2}

        try:
            resp = await self.client.get(f"{self.HISTORY_URL}/api/qt/stock/kline/get", params={
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "klt": klt_map.get(period, 101),
                "fqt": fqt_map.get(fq_type, 1),
                "beg": "0",
                "end": "20500101",
                "lmt": limit,
                "ut": "fa5fd1943c7b386f172d6893dbfd32",
            })
            result = resp.json()
            klines = result.get("data", {}).get("klines", [])
            if not klines:
                return None

            items = []
            for line in klines:
                parts = line.split(",")
                if len(parts) >= 6:
                    items.append({
                        "date": parts[0],
                        "open": float(parts[1]),
                        "close": float(parts[2]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "volume": int(float(parts[5])),
                        "amount": float(parts[6]) if len(parts) > 6 else 0,
                        "change_pct": float(parts[8]) if len(parts) > 8 else 0,
                    })

            return {
                "symbol": symbol,
                "period": period,
                "fq_type": fq_type,
                "items": items,
            }
        except Exception as e:
            logger.warning(f"东方财富获取 {symbol} K线失败: {e}")
            return None

    async def fetch_timeline(self, symbol: str) -> Optional[dict]:
        secid = self._get_secid(symbol)
        try:
            resp = await self.client.get(f"{self.HISTORY_URL}/api/qt/stock/trends2/get", params={
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "isc": 1,
                "ut": "fa5fd1943c7b386f172d6893dbfd32",
            })
            result = resp.json()
            data = result.get("data", {})
            if not data:
                return None

            trends = data.get("trends", [])
            prev_close = data.get("preClose", 0)
            points = []
            for line in trends:
                parts = line.split(",")
                if len(parts) >= 4:
                    points.append({
                        "time": parts[0].split(" ")[-1] if " " in parts[0] else parts[0],
                        "price": float(parts[1]),
                        "avg": float(parts[2]),
                        "volume": int(float(parts[3])),
                    })

            return {
                "symbol": symbol,
                "date": datetime.now().strftime("%Y%m%d"),
                "prev_close": prev_close,
                "points": points,
            }
        except Exception as e:
            logger.warning(f"东方财富获取 {symbol} 分时数据失败: {e}")
            return None

    async def fetch_orderbook(self, symbol: str) -> Optional[dict]:
        secid = self._get_secid(symbol)
        try:
            resp = await self.client.get(f"{self.BASE_URL}/api/qt/stock/get", params={
                "secid": secid,
                "fields": "f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35",
                "ut": "fa5fd1943c7b386f172d6893dbfd32",
            })
            data = resp.json().get("data", {})
            if not data:
                return None

            asks = [
                {"level": 5, "price": data.get("f27", 0), "volume": data.get("f28", 0)},
                {"level": 4, "price": data.get("f25", 0), "volume": data.get("f26", 0)},
                {"level": 3, "price": data.get("f23", 0), "volume": data.get("f24", 0)},
                {"level": 2, "price": data.get("f21", 0), "volume": data.get("f22", 0)},
                {"level": 1, "price": data.get("f19", 0), "volume": data.get("f20", 0)},
            ]
            bids = [
                {"level": 1, "price": data.get("f29", 0), "volume": data.get("f30", 0)},
                {"level": 2, "price": data.get("f31", 0), "volume": data.get("f32", 0)},
                {"level": 3, "price": data.get("f33", 0), "volume": data.get("f34", 0)},
                {"level": 4, "price": data.get("f35", 0), "volume": data.get("f36", 0)},
                {"level": 5, "price": data.get("f37", 0), "volume": data.get("f38", 0)},
            ]

            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "asks": asks,
                "bids": bids,
            }
        except Exception as e:
            logger.warning(f"东方财富获取 {symbol} 盘口失败: {e}")
            return None

    def _parse_quote(self, symbol: str, data: dict) -> dict:
        return {
            "symbol": symbol,
            "name": data.get("f58", ""),
            "market": self._get_market_prefix(symbol),
            "price": data.get("f43", 0) or 0,
            "change": data.get("f169", 0) or 0,
            "change_pct": data.get("f170", 0) or 0,
            "open": data.get("f44", 0) or 0,
            "high": data.get("f45", 0) or 0,
            "low": data.get("f46", 0) or 0,
            "prev_close": data.get("f60", 0) or 0,
            "volume": data.get("f47", 0) or 0,
            "amount": data.get("f48", 0) or 0,
            "turnover_rate": data.get("f168", 0) or 0,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        }