from abc import ABC, abstractmethod
from typing import Optional


class BaseCollector(ABC):
    """数据采集器抽象基类"""

    @abstractmethod
    async def fetch_quote(self, symbol: str) -> Optional[dict]:
        """获取单只股票实时行情"""
        pass

    @abstractmethod
    async def fetch_quote_list(self, page: int = 1, page_size: int = 20,
                               sort_by: str = "change_pct", sort_order: str = "desc",
                               market: str = "all") -> Optional[dict]:
        """获取行情列表"""
        pass

    @abstractmethod
    async def fetch_kline(self, symbol: str, period: str = "d",
                          fq_type: str = "front", limit: int = 120) -> Optional[dict]:
        """获取 K 线数据"""
        pass

    @abstractmethod
    async def fetch_timeline(self, symbol: str) -> Optional[dict]:
        """获取分时数据"""
        pass

    @abstractmethod
    async def fetch_orderbook(self, symbol: str) -> Optional[dict]:
        """获取盘口数据"""
        pass

    def _get_secid(self, symbol: str) -> str:
        """根据股票代码生成东方财富 secid 格式"""
        if symbol.startswith("6"):
            return f"1.{symbol}"
        else:
            return f"0.{symbol}"

    def _get_market_prefix(self, symbol: str) -> str:
        """获取市场前缀"""
        return "sh" if symbol.startswith("6") else "sz"