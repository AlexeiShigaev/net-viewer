FROM python:3.11.7-alpine

WORKDIR /mac-finder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false --local

COPY ./app/pyproject.toml ./app/poetry.lock /mac-finder/

RUN poetry install
