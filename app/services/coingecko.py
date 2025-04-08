# API calls to CoinGecko will be handled here
from typing import Optional

import httpx
from fastapi import HTTPException

from app.config import settings
from app.schemas import CryptocurrencyMetadata


async def validate_crypto_symbol(symbol: str) -> str:
    """Validate if a cryptocurrency symbol exists on Coingecko and if so, return its CoinGecko ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.COINGECKO_API_URL}/search", params={"query": symbol}
        )
        data = response.json()

        matching_coins = [
            coin
            for coin in data.get("coins", [])
            if coin.get("symbol", "").upper() == symbol.upper()
        ]

        if not matching_coins:
            raise HTTPException(
                status_code=404,
                detail=f"Cryptocurrency with symbol '{symbol}' not found on CoinGecko",
            )

        # The responses are already sorted in descending order by market cap
        return matching_coins[0].get("id")


async def get_coin_metadata(coin_id: str) -> CryptocurrencyMetadata:
    """Fetch detailed metadata for a coin by its Coingecko ID"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.COINGECKO_API_URL}/coins/{coin_id}",
            params={
                "market_data": "true",
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
            },
        )
        response_json = response.json()

        # I have no idea how reliable CoinGecko API is
        if "market_data" not in response_json:
            return CryptocurrencyMetadata(
                coingecko_id=coin_id,
                market_cap_rank=(
                    response_json["market_cap_rank"]
                    if "market_cap_rank" in response_json
                    else None
                ),
                metadata_timestamp=(
                    response_json["last_updated"]
                    if "last_updated" in response_json
                    else None
                ),
            )

        return CryptocurrencyMetadata(
            current_price_usd=(
                response_json["market_data"]["current_price"]["usd"]
                if "current_price" in response_json["market_data"]
                and "usd" in response_json["market_data"]["current_price"]
                else None
            ),
            price_change_percentage_24h=(
                response_json["market_data"]["price_change_percentage_24h"]
                if "price_change_percentage_24h" in response_json["market_data"]
                else None
            ),
            total_volume_usd=(
                response_json["market_data"]["total_volume"]["usd"]
                if "total_volume" in response_json["market_data"]
                and "usd" in response_json["market_data"]["total_volume"]
                else None
            ),
            market_cap_usd=(
                response_json["market_data"]["market_cap"]["usd"]
                if "market_cap" in response_json["market_data"]
                and "usd" in response_json["market_data"]["market_cap"]
                else None
            ),
            market_cap_rank=(
                response_json["market_cap_rank"]
                if "market_cap_rank" in response_json
                else None
            ),
            coingecko_id=coin_id,
            metadata_timestamp=(
                response_json["last_updated"]
                if "last_updated" in response_json
                else None
            ),
        )
