import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas


def get_all_cryptocurrencies(
    session: Session, limit: Optional[int] = None
) -> List[models.Cryptocurrency]:
    """
    Retrieve all cryptocurrencies up to a specified limit.
    """
    if limit is not None:
        return session.query(models.Cryptocurrency).limit(limit).all()
    return session.query(models.Cryptocurrency).all()


def get_cryptocurrency(
    session: Session, crypto_id: int
) -> Optional[models.Cryptocurrency]:
    """
    Retrieve a single cryptocurrency by its ID.
    """
    return (
        session.query(models.Cryptocurrency)
        .filter(models.Cryptocurrency.id == crypto_id)
        .first()
    )


def get_cryptocurrency_by_symbol(
    session: Session, symbol: str
) -> Optional[models.Cryptocurrency]:
    """
    Retrieve a single cryptocurrency by its symbol.
    """
    return (
        session.query(models.Cryptocurrency)
        .filter(models.Cryptocurrency.symbol == symbol)
        .first()
    )


def create_cryptocurrency(
    session: Session,
    crypto: schemas.CryptocurrencyCreate,
    metadata: Optional[schemas.CryptocurrencyMetadata],
) -> models.Cryptocurrency:
    """
    Create a new cryptocurrency record.
    """
    # Check if cryptocurrency with same symbol already exists
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=crypto.symbol)
    if db_crypto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cryptocurrency with symbol '{crypto.symbol}' already exists",
        )

    # Create new cryptocurrency instance
    db_crypto = models.Cryptocurrency(
        name=crypto.name,
        symbol=crypto.symbol,
        amount=crypto.amount,
    )

    # If metadata is provided, add it to the cryptocurrency instance
    if metadata is not None:
        db_crypto.crypto_metadata = models.CryptocurrencyMetadata(
            current_price_usd=metadata.current_price_usd,
            price_change_percentage_24h=metadata.price_change_percentage_24h,
            total_volume_usd=metadata.total_volume_usd,
            market_cap_usd=metadata.market_cap_usd,
            market_cap_rank=metadata.market_cap_rank,
            coingecko_id=metadata.coingecko_id,
            metadata_timestamp=metadata.metadata_timestamp,
        )

    try:
        session.add(db_crypto)
        session.commit()
        session.refresh(db_crypto)
        return db_crypto
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )


def update_cryptocurrency(
    session: Session, symbol: str, crypto: schemas.CryptocurrencyUpdate
) -> models.Cryptocurrency:
    """
    Update an existing cryptocurrency record.
    """
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    # Update fields
    if crypto.name is not None:
        db_crypto.name = crypto.name
    if crypto.amount is not None:
        db_crypto.amount = crypto.amount

    try:
        session.commit()
        session.refresh(db_crypto)
        return db_crypto
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred",
        )


def update_cryptocurrency_metadata(
    session: Session, symbol: str, new_metadata: schemas.CryptocurrencyMetadata
) -> models.Cryptocurrency:
    """
    Update the metadata of an existing cryptocurrency record.
    """
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    # Update metadata fields
    if new_metadata.current_price_usd is not None:
        db_crypto.crypto_metadata.current_price_usd = new_metadata.current_price_usd
    if new_metadata.price_change_percentage_24h is not None:
        db_crypto.crypto_metadata.price_change_percentage_24h = (
            new_metadata.price_change_percentage_24h
        )
    if new_metadata.total_volume_usd is not None:
        db_crypto.crypto_metadata.total_volume_usd = new_metadata.total_volume_usd
    if new_metadata.market_cap_usd is not None:
        db_crypto.crypto_metadata.market_cap_usd = new_metadata.market_cap_usd
    if new_metadata.market_cap_rank is not None:
        db_crypto.crypto_metadata.market_cap_rank = new_metadata.market_cap_rank
    if new_metadata.coingecko_id is not None:
        db_crypto.crypto_metadata.coingecko_id = new_metadata.coingecko_id
    if new_metadata.metadata_timestamp is not None:
        db_crypto.crypto_metadata.metadata_timestamp = new_metadata.metadata_timestamp

    # Force Cryptocurrency model to update the updated_at field
    db_crypto.updated_at = datetime.datetime.utcnow()

    session.commit()
    session.refresh(db_crypto)

    return db_crypto


def delete_cryptocurrency(session: Session, symbol: str) -> bool:
    """
    Delete a cryptocurrency record.
    Returns True if deletion was successful.
    """
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    session.delete(db_crypto)
    session.commit()
    return True


def delete_cryptocurrency_by_symbol(session: Session, symbol: str) -> bool:
    """
    Delete a cryptocurrency record by its symbol.
    Returns True if deletion was successful.
    """
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    session.delete(db_crypto)
    session.commit()
    return True
