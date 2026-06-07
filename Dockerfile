FROM node:20-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CODEX_HOME=/codex-home

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        less \
        python3 \
        python3-pip \
        ripgrep \
        vim-tiny \
    && npm install -g @openai/codex \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /codex-home /codex-default

COPY docker/codex/config.toml /codex-default/config.toml
COPY docker/codex/entrypoint.sh /usr/local/bin/codex-entrypoint
RUN chmod +x /usr/local/bin/codex-entrypoint

WORKDIR /workspace

ENTRYPOINT ["codex-entrypoint"]
CMD ["bash"]
