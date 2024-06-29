FROM python:latest as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN wget https://github.com/Kitware/CMake/releases/download/v3.29.6/cmake-3.29.6-linux-x86_64.tar.gz -O /tmp/cmake.tar.gz && \
    mkdir /tmp/cmake-dir && \
    tar -zxvf /tmp/cmake.tar.gz -C /tmp/cmake-dir --strip-components=1 && \ 
    cp /tmp/cmake-dir/bin/* /usr/local/bin && \
    cp -R /tmp/cmake-dir/share/* /usr/local/share

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:slim as runtime

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 wget tar git -y

RUN mkdir /app

RUN wget https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_amd64 -O /app/go2rtc
RUN chmod +x /app/go2rtc

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY src /app/src

ENTRYPOINT ["python", "-m", "src.main"]