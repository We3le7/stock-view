from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Date, Integer, Numeric, SmallInteger, func
from app.core.database import Base


class StockInfo(Base):
    __tablename__ = "stock_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    name = Column(String(20), nullable=False)
    market = Column(String(10), nullable=False)
    industry = Column(String(20))
    sector = Column(String(20))
    list_date = Column(Date)
    total_shares = Column(BigInteger)
    float_shares = Column(BigInteger)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class QuoteDaily(Base):
    __tablename__ = "quote_daily"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    trade_date = Column(Date, nullable=False)
    open = Column(Numeric(10, 3))
    high = Column(Numeric(10, 3))
    low = Column(Numeric(10, 3))
    close = Column(Numeric(10, 3))
    volume = Column(BigInteger)
    amount = Column(Numeric(18, 2))
    turnover_rate = Column(Numeric(8, 4))
    amplitude = Column(Numeric(8, 4))
    change_pct = Column(Numeric(8, 4))
    created_at = Column(DateTime, server_default=func.now())


class QuoteTick(Base):
    __tablename__ = "quote_tick"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    trade_date = Column(Date, nullable=False)
    tick_data = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, server_default=func.now())


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, default=1)
    symbol = Column(String(10), nullable=False)
    market = Column(String(10), nullable=False)
    sort_order = Column(Integer, default=0)
    group_name = Column(String(20), default="default")
    added_at = Column(DateTime, server_default=func.now())


class AIAnalysisLog(Base):
    __tablename__ = "ai_analysis_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    analysis_type = Column(String(20), nullable=False)
    model_version = Column(String(20), nullable=False)
    request_params = Column(String)  # JSON
    result_data = Column(String)  # JSON
    trend = Column(String(10))
    confidence = Column(Numeric(4, 2))
    duration_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())