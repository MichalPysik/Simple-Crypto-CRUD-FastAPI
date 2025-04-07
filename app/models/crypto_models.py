# The database models for the cryptocurrencies will be
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Updates when metadata is updated or when the name is changed
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 'metadata' name is reserved in SQLAlchemy
    crypto_metadata = relationship(
        "CryptocurrencyMetadata", back_populates="cryptocurrency", uselist=False
    )


class CryptocurrencyMetadata(Base):
    __tablename__ = "cryptocurrency_metadata"

    id = Column(Integer, primary_key=True, index=True)
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"), unique=True)

    current_price_usd = Column(Float)
    price_change_percentage_24h = Column(Float)
    total_volume_usd = Column(Float)
    market_cap_usd = Column(Float)
    market_cap_rank = Column(Integer)

    coingecko_id = Column(String)
    metadata_timestamp = Column(DateTime(timezone=True)) # Value fetched from Coingecko API

    cryptocurrency = relationship("Cryptocurrency", back_populates="crypto_metadata")
