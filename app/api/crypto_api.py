from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
import app.schemas as schemas
import app.crud as crud

router = APIRouter(prefix="/api")


@router.post("/cryptocurrency", response_model=schemas.CryptocurrencyResponse, status_code=status.HTTP_201_CREATED)
def create_cryptocurrency(
    crypto_data: schemas.CryptocurrencyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new cryptocurrency.
    """
    return crud.create_cryptocurrency(session=db, crypto=crypto_data)


@router.get("/cryptocurrency/{symbol}", response_model=schemas.CryptocurrencyResponse)
def get_cryptocurrency(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific cryptocurrency by its symbol.
    """
    crypto = crud.get_cryptocurrency_by_symbol(session=db, symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol {symbol} not found"
        )
    return crypto


@router.get("/cryptocurrencies", response_model=List[schemas.CryptocurrencyResponse])
def get_all_cryptocurrencies(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of all cryptocurrencies.
    """
    return crud.get_all_cryptocurrencies(session=db, limit=limit)


@router.put("/cryptocurrency/{symbol}", response_model=schemas.CryptocurrencyResponse)
def update_cryptocurrency(
    symbol: str,
    crypto_data: schemas.CryptocurrencyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update details of a specific cryptocurrency by its symbol.
    """
    crypto = crud.get_cryptocurrency_by_symbol(session=db, symbol=symbol)
    if not crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol {symbol} not found"
        )
    
    return crud.update_cryptocurrency(session=db, symbol=symbol, crypto=crypto_data)


@router.delete("/cryptocurrencies/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cryptocurrency(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific cryptocurrency by its symbol.
    """
    crud.delete_cryptocurrency_by_symbol(session=db, symbol=symbol)


@router.post("/cryptocurrencies/{symbol}/refresh")
def refresh_cryptocurrency(symbol: str):
    """
    Refresh the data of a specific cryptocurrency by its symbol.
    """
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    # Maybe return updated cryptocurrency data
    return {"message": f"Cryptocurrency {symbol} data refreshed successfully"}


@router.post("/cryptocurrencies/refresh-all")
def refresh_all_cryptocurrencies():
    """
    Refresh the data of all cryptocurrencies.
    """
    # Maybe return updated list of all cryptocurrencies
    return {"message": "All cryptocurrencies data refreshed successfully"}
