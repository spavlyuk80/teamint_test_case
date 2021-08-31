# TEAMINTERNATIONAL TEST CASE

##Requirements

This project had been tested in Ubuntu 20.04 with Python 3.8
Requirements:
- Python 3.8
- docker and docker-compose
- pipenv (you can install it with pip install pipenv)
- .env file has all the credentials, including keys for hunter.io and clearbit
services as well as . These keys will be deleted (keys revoked)
by the Sept 20, 2021

##Startup

1. run `docker-compose up` from the backend/ folder. This will start django server, a celery worker, beat server and
Postgres database. The migrations and superuser will be created automatically. For credentials, please see env file.
2. from backend/ folder activate virtual environment with `pipenv shell`, then install modules with `pipenv install`
3. run `python autobot.py` from backend/ folder. The bot prints some extensive debug information as well as summary of
the final result.

## Other info
there is also a json file `thunder-collection_restapi.json` with openapi configuration of the API (not extensively tested)

