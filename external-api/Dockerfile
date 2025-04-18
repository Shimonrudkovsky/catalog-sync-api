FROM python:3.11-slim

WORKDIR /external-api

RUN apt-get update && apt-get install -y \
    curl gcc libpq-dev \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

COPY ./ /external-api

RUN poetry install --no-interaction --no-root

EXPOSE ${APP_PORT}

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
