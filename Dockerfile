FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

RUN apt update && \
    pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false

RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY . .

RUN poetry install

CMD ["python3", "main.py"]