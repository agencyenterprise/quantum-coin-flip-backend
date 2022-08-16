# Quantum Coin Flip - Backend

## How to run this Project

Make sure you have pipenv installed:

`brew install pipenv`

Install the dependencies:

`pipenv install`

Copy the .env.sample to a .env file. If you want to run against real APIs, then replace the API keys with real API keys. Otherwise, just leave `MOCK_BACKEND` as `true`.

Start up your mongo DB locally:

`docker-compose up -d`

If you want to run a script, do it like so:

`pipenv run python app/getCoinFlips.py`

Or if you want to test that it works in Heroku:

`heroku run python getCoinFlips.py`
