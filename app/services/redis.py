import json
import logging
from typing import Optional

from redis import Redis

import app.models as models
import app.schemas as schemas
from app.config import settings

logger = logging.getLogger(__name__)

redis_client = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


def check_crypto_in_cache(symbol: str) -> bool:
    """Check if cryptocurrency data exists in Redis cache"""
    return redis_client.exists(symbol) > 0


def get_crypto_from_cache(symbol: str) -> Optional[schemas.CryptocurrencyResponse]:
    """Get cryptocurrency data from Redis cache"""
    data = redis_client.get(symbol)
    if data:
        logger.info(f"Retrieved cryptocurrency '{symbol}' from Redis cache")
        return json.loads(data)
    logger.info(f"Failed to retrieve cryptocurrency '{symbol}' from Redis cache")
    return None


def insert_crypto_to_cache(
    symbol: str, model: models.Cryptocurrency, expiration: int = 3600
):
    """Insert cryptocurrency data in Redis cache with expiration (default 1 hour)"""
    # Convert the model instance to the schema
    value = schemas.CryptocurrencyResponse.from_orm(model)
    redis_client.setex(symbol, expiration, json.dumps(value.model_dump(), default=str))
    logger.info(
        f"Inserted cryptocurrency '{symbol}' into Redis cache with expiration of {expiration} seconds"
    )


def delete_crypto_from_cache(symbol: str):
    """Delete cryptocurrency data from Redis cache"""
    redis_client.delete(symbol)
    logger.info(f"Deleted cryptocurrency '{symbol}' from Redis cache")
