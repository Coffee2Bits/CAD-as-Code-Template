FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Base image ships a Yarn apt source whose key can go stale and break apt-get update.
RUN rm -f /etc/apt/sources.list.d/yarn.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    libgl1 \
    libglx-mesa0 \
    libegl1 \
    libxrender1 \
    libxext6 \
    libxi6 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip uv

ARG DAGGER_VERSION=0.21.4
RUN curl -fsSL https://dl.dagger.io/dagger/install.sh | \
    DAGGER_VERSION=${DAGGER_VERSION} BIN_DIR=/usr/local/bin sh

ARG JUST_VERSION=1.52.0
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | \
    bash -s -- --tag ${JUST_VERSION} --to /usr/local/bin
