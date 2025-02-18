FROM python:3.12.9-slim

LABEL maintainer="cro7 <cro7nis@gmail.com>"
ENV APP="akash_x_bot"

RUN apt update \
    && apt install -y \
        tzdata \
        curl \
        jq \
        ffmpeg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /opt/$APP
WORKDIR /opt/$APP

WORKDIR /opt/$APP
RUN pip install poetry
COPY pyproject.toml pyproject.toml
COPY  poetry.lock  poetry.lock
RUN  poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction \
    && rm -rf /root/.cache/pypoetry

COPY configs/ configs/
COPY src/ .

ENTRYPOINT ["python", "app.py"]