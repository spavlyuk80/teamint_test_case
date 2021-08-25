FROM python:3.8-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y install libpq-dev gcc && pip install psycopg2

COPY ./restapi /usr/src/app/
WORKDIR /usr/src/app/
COPY Pipfile /usr/src/app/
COPY Pipfile.lock /usr/src/app/
RUN pip install pipenv
RUN pipenv install --system

EXPOSE 8081