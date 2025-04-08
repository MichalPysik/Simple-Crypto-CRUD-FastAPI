# Simple-Crypto-CRUD-FastAPI

## How to run
- Make sure you have Docker and Docker Compose installed.
- Configure settings in `docker-compose.yml` file and in `app/config.py` file.
- Make sure you are in the root directory of the project.
- Type 'docker compose build && docker compose up' in the terminal.

## What's implemented
- CRUD operations for crypto currencies, each identified by symbol (case insensitive).
- Only currencies that can be found via the CoinGecko API can be added.
- Both manual (manual trigger, when new crypto is added) and automatic (every 5 minutes) metadata fetching from CoinGecko API.
- Redis caching of crypto data for less frequent database quering.

## What could be added or improved
- Add tests.
- Allow multiple users, add user management.
- Implement frontend.

## Endpoints
- POST /api/cryptocurrency - Add a new cryptocurrency to the system. Specify the symbol that must be found in the CoinGecko API. Also specify the name and amount of the currency owned by the user.

- GET /api/cryptocurrency/{symbol} - Get the details, including metadata from CoinGecko API, of a specific cryptocurrency identified by its symbol.

- PUT /api/cryptocurrency/{symbol} - Update the details of a specific cryptocurrency by identified by its symbol. You can update the name and amount of the currency owned by the user (the metadata can only be updated via CoinGecko API calls).

- GET /api/cryptocurrencies - Get a list of all cryptocurrencies in the system, including their metadata.

- DELETE /api/cryptocurrency/{symbol} - Delete a specific cryptocurrency (and its metadata) identified by its symbol from the system.

- POST /api/cryptocurrency/{symbol}/refresh - Manually refresh the metadata of a specific cryptocurrency identified by its symbol. This will manually trigger a call to the CoinGecko API to fetch the latest metadata for that cryptocurrency.

- POST /api/cryptocurrencies/refresh - Manually refresh the metadata of all cryptocurrencies in the system. This will manually trigger the task which is normally scheduled to run every settings.REFRESH_INTERVAL_MINUTES minutes (see '/app/config.py' to change the interval).