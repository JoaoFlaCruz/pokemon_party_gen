#!/bin/sh
set -eu

mkdir -p "${CODEX_HOME:-/codex-home}"

if [ ! -f "${CODEX_HOME:-/codex-home}/config.toml" ]; then
    cp /codex-default/config.toml "${CODEX_HOME:-/codex-home}/config.toml"
fi

exec "$@"
