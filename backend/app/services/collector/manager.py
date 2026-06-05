import logging
from typing import Optional
from app.services.collector.base import BaseCollector
from app.services.collector.eastmoney import EastMoneyCollector
from app.services.collector.sina import SinaCollector

logger = logging.getLogger(__name__)

COLLECTOR_PRIORITY = ["eastmoney", "sina"]


class CollectorManager:
    """数据采集管理器 - 自动故障转移"""

    def __init__(self):
        self.collectors: dict[str, BaseCollector] = {
            "eastmoney": EastMoneyCollector(),
            "sina": SinaCollector(),
        }

    async def fetch_quote(self, symbol: str) -> Optional[dict]:
        for name in COLLECTOR_PRIORITY:
            try:
                collector = self.collectors[name]
                data = await collector.fetch_quote(symbol)
                if data:
                    return data
                logger.info(f"数据源 {name} 返回 {symbol} 空数据，尝试下一个数据源")
            except Exception as e:
                logger.warning(f"数据源 {name} 获取 {symbol} 行情失败: {e}")
                continue
        logger.error(f"所有数据源获取 {symbol} 行情均失败")
        return None

    async def fetch_quote_list(self, **kwargs) -> Optional[dict]:
        for name in COLLECTOR_PRIORITY:
            try:
                collector = self.collectors[name]
                data = await collector.fetch_quote_list(**kwargs)
                if data:
                    return data
                logger.info(f"数据源 {name} 返回行情列表空数据，尝试下一个数据源")
            except Exception as e:
                logger.warning(f"数据源 {name} 获取行情列表失败: {e}")
                continue
        logger.error("所有数据源获取行情列表均失败")
        return None

    async def fetch_kline(self, symbol: str, **kwargs) -> Optional[dict]:
        for name in COLLECTOR_PRIORITY:
            try:
                collector = self.collectors[name]
                data = await collector.fetch_kline(symbol, **kwargs)
                if data:
                    return data
                logger.info(f"数据源 {name} 返回 {symbol} K线空数据，尝试下一个数据源")
            except Exception as e:
                logger.warning(f"数据源 {name} 获取 {symbol} K线失败: {e}")
                continue
        logger.error(f"所有数据源获取 {symbol} K线均失败")
        return None

    async def fetch_timeline(self, symbol: str) -> Optional[dict]:
        for name in COLLECTOR_PRIORITY:
            try:
                collector = self.collectors[name]
                data = await collector.fetch_timeline(symbol)
                if data:
                    return data
                logger.info(f"数据源 {name} 返回 {symbol} 分时空数据，尝试下一个数据源")
            except Exception as e:
                logger.warning(f"数据源 {name} 获取 {symbol} 分时失败: {e}")
                continue
        logger.error(f"所有数据源获取 {symbol} 分时均失败")
        return None

    async def fetch_orderbook(self, symbol: str) -> Optional[dict]:
        for name in COLLECTOR_PRIORITY:
            try:
                collector = self.collectors[name]
                data = await collector.fetch_orderbook(symbol)
                if data:
                    return data
                logger.info(f"数据源 {name} 返回 {symbol} 盘口空数据，尝试下一个数据源")
            except Exception as e:
                logger.warning(f"数据源 {name} 获取 {symbol} 盘口失败: {e}")
                continue
        logger.error(f"所有数据源获取 {symbol} 盘口均失败")
        return None


# 全局单例
collector_manager = CollectorManager()
