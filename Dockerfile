FROM python:3.12-slim

WORKDIR /app

# Configurar zona horaria de Madrid
ENV TZ=Europe/Madrid
RUN apt-get update && apt-get install -y \
    build-essential \
    tzdata \
    && ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv \
    && mkdir -p logs database

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "main.py"]
