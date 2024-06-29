
FROM python:latest AS builder

ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN echo "I am running on $BUILDPLATFORM, building for $TARGETPLATFORM"

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN case "$TARGETPLATFORM" in \
        "linux/amd64") \
            URL="https://github.com/Kitware/CMake/releases/latest/download/cmake-3.29.6-linux-x86_64.tar.gz" \
            ;; \
        "linux/arm64") \
            URL="https://github.com/Kitware/CMake/releases/latest/download/cmake-3.29.6-linux-aarch64.tar.gz" \
            ;; \
        *) \
            echo "Unsupported TARGETPLATFORM: $TARGETPLATFORM" && exit 1 \
            ;; \
    esac && \ 
    wget -O /tmp/cmake.tar.gz "$URL" && \
    mkdir /tmp/cmake-dir && \
    tar -zxvf /tmp/cmake.tar.gz -C /tmp/cmake-dir --strip-components=1 && \ 
    cp /tmp/cmake-dir/bin/* /usr/local/bin && \
    cp -R /tmp/cmake-dir/share/* /usr/local/share

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:slim AS runtime

ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN echo "I am running on $BUILDPLATFORM, building for $TARGETPLATFORM"

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 wget tar git -y

RUN mkdir /app

RUN case "$TARGETPLATFORM" in \
        "linux/amd64") \
            URL="https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_amd64" \
            ;; \
        "linux/arm64") \
            URL="https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64" \
            ;; \
        *) \
            echo "Unsupported TARGETPLATFORM: $TARGETPLATFORM" && exit 1 \
            ;; \
    esac && \  
    wget -O /app/go2rtc "$URL"
RUN chmod +x /app/go2rtc

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY src /app/src

ENTRYPOINT ["python", "-m", "src.main"]