from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from core.database import Base

class ETLCheckpoint(Base):
    __tablename__ = "etl_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)
    meta_data = Column(JSON, nullable=True) # e.g. file hash, line number
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ETLRun(Base):
    __tablename__ = "etl_runs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    status = Column(String) # success, failed
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    records_processed = Column(Integer, default=0)
    error_message = Column(String, nullable=True)

class RawCoinGecko(Base):
    __tablename__ = "raw_coingecko"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    data = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class RawCoinPaprika(Base):
    __tablename__ = "raw_coinpaprika"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    data = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())



class RawCSVUpload(Base):
    __tablename__ = "raw_csv_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    symbol = Column(String)
    price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime)
    source = Column(String)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class RawLegacyUpload(Base):
    __tablename__ = "raw_legacy_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    ticker = Column(String)
    last_price = Column(Float)
    vol = Column(Float)
    recorded_date = Column(String) 
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class CryptoMarketData(Base):
    __tablename__ = "crypto_market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price_usd = Column(Float)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), index=True)
    source = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite unique constraint for idempotency
    __table_args__ = (
        UniqueConstraint('symbol', 'recorded_at', 'source', name='uq_crypto_market_data_entry'),
    )
