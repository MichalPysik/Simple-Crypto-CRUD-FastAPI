import logging
from typing import List

import app.crud as crud
from app.db import get_db
from app.schemas import CryptocurrencyResponse
from app.services.coingecko import get_coin_metadata
from app.services.redis import (check_crypto_in_cache,
                                delete_crypto_from_cache,
                                insert_crypto_to_cache)

logger = logging.getLogger(__name__)


async def refresh_all_cryptocurrencies_metadata():
    """
    Task to refresh the metadata of all cryptocurrencies.
    This task can be scheduled to run periodically or called manually from the API.

    The task always creates its own database session to ensure it works correctly
    when triggered by the scheduler.
    """
    # Always create a new session for scheduled tasks
    db = next(get_db())
    logger.info("Started cryptocurrency metadata refresh task")

    try:
        # Get all cryptocurrencies from the database
        all_cryptos = crud.get_all_cryptocurrencies(session=db)

        for i, crypto in enumerate(all_cryptos):
            # Fetch metadata from CoinGecko
            new_metadata = await get_coin_metadata(crypto.crypto_metadata.coingecko_id)

            # Update the metadata in the database (and update the cache)
            updated_crypto = crud.update_cryptocurrency_metadata(
                session=db, symbol=crypto.symbol, new_metadata=new_metadata
            )
            if check_crypto_in_cache(crypto.symbol):
                delete_crypto_from_cache(crypto.symbol)
            insert_crypto_to_cache(symbol=crypto.symbol, model=updated_crypto)

            logger.info(
                f"Updated metadata for '{crypto.symbol}', progress: {i + 1}/{len(all_cryptos)}"
            )

        logger.info(
            f"Completed cryptocurrency metadata refresh for all {len(all_cryptos)} coins"
        )
    finally:
        db.close()
        logger.info("Closed database connection for cryptocurrency refresh task")
