from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

import app.models as models
import app.schemas as schemas


def get_all_cryptocurrencies(session: Session, limit: int = 100) -> List[models.Cryptocurrency]:
    """
    Retrieve all cryptocurrencies up to a specified limit.
    """
    return session.query(models.Cryptocurrency).limit(limit).all()


def get_cryptocurrency(session: Session, crypto_id: int) -> Optional[models.Cryptocurrency]:
    """
    Retrieve a single cryptocurrency by its ID.
    """
    return session.query(models.Cryptocurrency).filter(models.Cryptocurrency.id == crypto_id).first()


def get_cryptocurrency_by_symbol(session: Session, symbol: str) -> Optional[models.Cryptocurrency]:
    """
    Retrieve a single cryptocurrency by its symbol.
    """
    return session.query(models.Cryptocurrency).filter(models.Cryptocurrency.symbol == symbol).first()


def create_cryptocurrency(session: Session, crypto: schemas.CryptocurrencyCreate) -> models.Cryptocurrency:
    """
    Create a new cryptocurrency record.
    """
    # Check if cryptocurrency with same symbol already exists
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=crypto.symbol)
    if db_crypto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cryptocurrency with symbol '{crypto.symbol}' already exists"
        )
    
    # Create new cryptocurrency instance
    db_crypto = models.Cryptocurrency(
        name=crypto.name,
        symbol=crypto.symbol
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
            detail="Database integrity error occurred"
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
            detail=f"Cryptocurrency with symbol '{symbol}' not found"
        )
    
    # Update name field
    if crypto.name:
        db_crypto.name = crypto.name
    
    try:
        session.commit()
        session.refresh(db_crypto)
        return db_crypto
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error occurred"
        )


def delete_cryptocurrency(session: Session, symbol: str) -> bool:
    """
    Delete a cryptocurrency record.
    Returns True if deletion was successful.
    """
    db_crypto = get_cryptocurrency_by_symbol(session, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found"
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
            detail=f"Cryptocurrency with symbol '{symbol}' not found"
        )
    
    session.delete(db_crypto)
    session.commit()
    return True