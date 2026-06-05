import random
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    TECHNICAL = "technical"
    TREND_PREDICTION = "trend"
    RISK_ASSESSMENT = "risk"
    COMPREHENSIVE = "comprehensive"


class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class AIInterface(ABC):
    """AI 分析抽象接口"""

    @abstractmethod
    async def analyze(self, symbol: str, analysis_type: str, period_days: int = 30) -> dict:
        pass

    @abstractmethod
    async def stream_analyze(self, symbol: str, analysis_type: str, period_days: int = 30):
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        pass


class MockAIAdapter(AIInterface):
    """Mock AI 适配器"""

    async def analyze(self, symbol: str, analysis_type: str, period_days: int = 30) -> dict:
        trend = random.choice(list(TrendDirection))
        confidence = round(random.uniform(0.55, 0.92), 2)
        return {
            "symbol": symbol,
            "analysis_type": analysis_type,
            "trend": trend.value,
            "confidence": confidence,
            "summary": f"[Mock] 对 {symbol} 的模拟分析结果，仅供参考。当前趋势偏{'强' if trend == TrendDirection.BULLISH else '弱' if trend == TrendDirection.BEARISH else '中性'}，置信度 {confidence}",
            "details": {
                "technical": {
                    "MACD": {"signal": "golden_cross" if random.random() > 0.5 else "death_cross",
                             "value": round(random.uniform(-0.05, 0.05), 3),
                             "description": "MACD金叉形成" if random.random() > 0.5 else "MACD死叉形成"},
                    "KDJ": {"signal": "overbought" if random.random() > 0.5 else "oversold",
                            "value": round(random.uniform(20, 85), 1),
                            "description": "KDJ指标处于超买区域" if random.random() > 0.5 else "KDJ指标处于超卖区域"},
                    "RSI": {"signal": "neutral", "value": round(random.uniform(35, 70), 1),
                            "description": "RSI处于中性区域"},
                    "BOLL": {"signal": "mid_band", "value": round(random.uniform(5, 50), 2),
                             "description": "价格运行在布林带中轨附近"},
                },
                "support_resistance": {
                    "support_levels": [round(random.uniform(5, 10), 2) for _ in range(3)],
                    "resistance_levels": [round(random.uniform(10, 20), 2) for _ in range(3)],
                },
                "prediction": {
                    "direction": trend.value,
                    "target_price": round(random.uniform(8, 20), 2),
                    "stop_loss": round(random.uniform(5, 8), 2),
                    "timeframe": "5个交易日",
                },
            },
            "indicators": {
                "MACD": {"DIF": round(random.uniform(-0.1, 0.1), 3), "DEA": round(random.uniform(-0.1, 0.1), 3), "MACD": round(random.uniform(-0.05, 0.05), 3)},
                "KDJ": {"K": round(random.uniform(20, 90), 1), "D": round(random.uniform(20, 90), 1), "J": round(random.uniform(10, 100), 1)},
                "RSI": round(random.uniform(30, 75), 1),
                "BOLL": {"upper": round(random.uniform(10, 20), 2), "mid": round(random.uniform(5, 15), 2), "lower": round(random.uniform(3, 10), 2)},
            },
            "risk_level": random.choice(["low", "medium", "high"]),
            "timestamp": datetime.now().isoformat(),
            "model_version": "mock-v1.0",
        }

    async def stream_analyze(self, symbol: str, analysis_type: str, period_days: int = 30):
        steps = [
            ("collecting_data", 0.2, "正在收集行情数据..."),
            ("computing_indicators", 0.5, "正在计算技术指标..."),
            ("model_inference", 0.8, "AI模型推理中..."),
        ]
        for step, progress, message in steps:
            yield {"type": "progress", "step": step, "progress": progress, "message": message}
            await asyncio.sleep(0.3)
        result = await self.analyze(symbol, analysis_type, period_days)
        yield {"type": "result", "data": result}

    def get_model_info(self) -> dict:
        return {
            "name": "MockAI",
            "version": "mock-v1.0",
            "description": "模拟AI适配器，返回随机数据",
            "supported_types": [t.value for t in AnalysisType],
            "status": "active",
        }


class RuleEngineAdapter(AIInterface):
    """规则引擎适配器 - 基于简单技术指标规则"""

    async def analyze(self, symbol: str, analysis_type: str, period_days: int = 30) -> dict:
        from app.services.collector.manager import collector_manager
        kline_data = await collector_manager.fetch_kline(symbol, period="d", limit=period_days)

        # 简单规则分析
        score = 0
        indicators = {}

        if kline_data and kline_data.get("items"):
            items = kline_data["items"]
            if len(items) >= 2:
                last = items[-1]
                prev = items[-2]
                if last["close"] > last["open"]:
                    score += 1
                if last["close"] > prev["close"]:
                    score += 1
                if last["volume"] > prev["volume"]:
                    score += 1

            if len(items) >= 5:
                ma5 = sum(i["close"] for i in items[-5:]) / 5
                if items[-1]["close"] > ma5:
                    score += 2

            if len(items) >= 20:
                ma20 = sum(i["close"] for i in items[-20:]) / 20
                if items[-1]["close"] > ma20:
                    score += 2

        if score >= 4:
            trend = TrendDirection.BULLISH
        elif score <= 1:
            trend = TrendDirection.BEARISH
        else:
            trend = TrendDirection.NEUTRAL

        confidence = min(0.5 + score * 0.08, 0.95)

        return {
            "symbol": symbol,
            "analysis_type": analysis_type,
            "trend": trend.value,
            "confidence": round(confidence, 2),
            "summary": f"基于均线与量价规则分析，{symbol} 当前趋势{'偏强' if trend == TrendDirection.BULLISH else '偏弱' if trend == TrendDirection.BEARISH else '中性'}，得分 {score}/7",
            "details": {
                "technical": {
                    "score": score,
                    "rules_triggered": ["收阳线" if score > 0 else "收阴线", "量价配合" if score > 2 else "量价背离"],
                },
                "prediction": {"direction": trend.value, "timeframe": "5个交易日"},
            },
            "indicators": indicators,
            "risk_level": "low" if score >= 4 else "medium" if score >= 2 else "high",
            "timestamp": datetime.now().isoformat(),
            "model_version": "rule-v1.0",
        }

    async def stream_analyze(self, symbol: str, analysis_type: str, period_days: int = 30):
        yield {"type": "progress", "step": "collecting_data", "progress": 0.3, "message": "正在获取K线数据..."}
        await asyncio.sleep(0.2)
        yield {"type": "progress", "step": "computing_indicators", "progress": 0.7, "message": "正在计算技术指标..."}
        await asyncio.sleep(0.2)
        result = await self.analyze(symbol, analysis_type, period_days)
        yield {"type": "result", "data": result}

    def get_model_info(self) -> dict:
        return {
            "name": "RuleEngine",
            "version": "rule-v1.0",
            "description": "基于技术指标规则的分析方法",
            "supported_types": [t.value for t in AnalysisType],
            "status": "active",
        }


def create_ai_adapter(adapter_name: str = "mock") -> AIInterface:
    adapter_map = {
        "mock": MockAIAdapter,
        "rule": RuleEngineAdapter,
    }
    cls = adapter_map.get(adapter_name, MockAIAdapter)
    return cls()