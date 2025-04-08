import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db
from app.services.coingecko import get_coin_metadata, validate_crypto_symbol
from app.services.redis import *

router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)


@router.post(
    "/cryptocurrency",
    response_model=schemas.CryptocurrencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_cryptocurrency(
    crypto_data: schemas.CryptocurrencyCreate, db: Session = Depends(get_db)
):
    """
    Create a new cryptocurrency.
    """
    # Convert symbol to uppercase, to avoid multiple coins with the same Coingecko IDs
    crypto_data.symbol = crypto_data.symbol.upper()

    # Check if the cryptocurrency exists on CoinGecko
    coingecko_id = await validate_crypto_symbol(crypto_data.symbol)
    logger.info(
        f"Matching symbol found on CoinGecko. Symbol: {crypto_data.symbol}, CoinGecko ID: {coingecko_id}"
    )

    # Fetch metadata from CoinGecko
    coin_metadata = await get_coin_metadata(coingecko_id)

    new_crypto = crud.create_cryptocurrency(
        session=db, crypto=crypto_data, metadata=coin_metadata
    )
    insert_crypto_to_cache(
        symbol=crypto_data.symbol,
        model=new_crypto,
    )
    return new_crypto


@router.get("/cryptocurrency/{symbol}", response_model=schemas.CryptocurrencyResponse)
def get_cryptocurrency(symbol: str, db: Session = Depends(get_db)):
    """
    Get details of a specific cryptocurrency by its symbol.
    """
    symbol = symbol.upper()  # Ensure the symbol is in uppercase

    if check_crypto_in_cache(symbol):
        return get_crypto_from_cache(symbol)

    crypto = crud.get_cryptocurrency_by_symbol(session=db, symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )
    return crypto


@router.get("/cryptocurrencies", response_model=List[schemas.CryptocurrencyResponse])
def get_all_cryptocurrencies(
    limit: Optional[int] = None, db: Session = Depends(get_db)
):
    """
    Get a list of all cryptocurrencies.
    """
    return crud.get_all_cryptocurrencies(session=db, limit=limit)


@router.put("/cryptocurrency/{symbol}", response_model=schemas.CryptocurrencyResponse)
def update_cryptocurrency(
    symbol: str,
    crypto_data: schemas.CryptocurrencyUpdate,
    db: Session = Depends(get_db),
):
    """
    Update details of a specific cryptocurrency by its symbol.
    """
    symbol = symbol.upper()  # Ensure the symbol is in uppercase

    crypto = crud.get_cryptocurrency_by_symbol(session=db, symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol {symbol} not found",
        )

    updated_crypto = crud.update_cryptocurrency(
        session=db, symbol=symbol, crypto=crypto_data
    )

    if check_crypto_in_cache(symbol):
        delete_crypto_from_cache(symbol)
    insert_crypto_to_cache(symbol=symbol, model=updated_crypto)

    return updated_crypto


@router.delete("/cryptocurrencies/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cryptocurrency(symbol: str, db: Session = Depends(get_db)):
    """
    Delete a specific cryptocurrency by its symbol.
    """
    symbol = symbol.upper()  # Ensure the symbol is in uppercase

    crud.delete_cryptocurrency_by_symbol(session=db, symbol=symbol)

    if check_crypto_in_cache(symbol):
        delete_crypto_from_cache(symbol)


@router.post(
    "/cryptocurrencies/{symbol}/refresh", response_model=schemas.CryptocurrencyResponse
)
async def refresh_cryptocurrency_metadata(symbol: str, db: Session = Depends(get_db)):
    """
    Refresh the data of a specific cryptocurrency by its symbol.
    """
    symbol = symbol.upper()  # Ensure the symbol is in uppercase

    # Get the cryptocurrency from the database
    crypto = crud.get_cryptocurrency_by_symbol(session=db, symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    new_metadata = await get_coin_metadata(crypto.crypto_metadata.coingecko_id)

    # Update the metadata in the database and return the updated cryptocurrency
    updated_crypto = crud.update_cryptocurrency_metadata(
        session=db, symbol=symbol, new_metadata=new_metadata
    )

    # Update the cache
    if check_crypto_in_cache(symbol):
        delete_crypto_from_cache(symbol)
    insert_crypto_to_cache(symbol=symbol, model=updated_crypto)

    return updated_crypto


@router.post(
    "/cryptocurrencies/refresh-all", response_model=List[schemas.CryptocurrencyResponse]
)
async def refresh_all_cryptocurrencies_metada(db: Session = Depends(get_db)):
    """
    Refresh the data of all cryptocurrencies.
    """
    # Get all cryptocurrencies from the database
    all_cryptos = crud.get_all_cryptocurrencies(session=db)

    response_list = []
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

        response_list.append(updated_crypto)
        logger.info(
            f"Updated metadata for '{crypto.symbol}', progress: {i + 1}/{len(all_cryptos)}"
        )

    return response_list
