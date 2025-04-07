from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CryptocurrencyBase(BaseModel):
    """Base model with common cryptocurrency attributes"""

    symbol: str = Field(
        ...,
        description="Cryptocurrency symbol (e.g., BTC, ETH)",
        min_length=1,
        max_length=10,
    )
    name: str = Field(
        ..., description="Full name of the cryptocurrency", min_length=1, max_length=100
    )


class CryptocurrencyCreate(CryptocurrencyBase):
    """Model for creating a new cryptocurrency"""
    pass


class CryptocurrencyUpdate(BaseModel):
    """Model for updating an existing cryptocurrency"""
    # Only name can be updated, as update doesn't even make much sense here
    name: Optional[str] = Field(
        None, description="Full name of the cryptocurrency", min_length=1, max_length=100
    )


class CryptocurrencyMetadata(BaseModel):
    """Model for cryptocurrency metadata from Coingecko"""

    current_price_usd: float = Field(None, description="Current price in USD")
    price_change_percentage_24h: Optional[float] = Field(
        None, description="24h price change percentage"
    )
    total_volume_usd: Optional[float] = Field(None, description="24h trading volume")
    market_cap_usd: float = Field(None, description="Market capitalization in USD")
    market_cap_rank: Optional[int] = Field(None, description="Market cap rank")

    coingecko_id: str = Field(None, description="CoinGecko ID for the cryptocurrency")
    metadata_timestamp: Optional[datetime] = Field(
        None, description="Datetime fetched from Coingecko API, corresponding to the actuality of the data"
    )
    last_checked: Optional[datetime] = Field(
        None, description="When the metadata was last fetched from Coingecko API"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Cryptocurrency(CryptocurrencyBase):
    """Complete cryptocurrency model including database fields"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CryptocurrencyResponse(Cryptocurrency):
    """Response model including metadata"""

    metadata: Optional[CryptocurrencyMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "created_at": "2025-04-07T14:00:00",
                    "updated_at": "2025-04-07T14:00:00",
                    "metadata": {
                        "current_price": 66421.0,
                        "market_cap": 1320000000000.0,
                        "market_cap_rank": 1,
                        "total_volume": 42000000000.0,
                        "price_change_24h": 1200.0,
                        "price_change_percentage_24h": 1.75,
                        "coingecko_id": "bitcoin",
                        "last_updated_at": "2025-04-07T14:00:00",
                    },
                }
            ]
        }
    }
