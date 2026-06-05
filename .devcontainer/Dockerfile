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
