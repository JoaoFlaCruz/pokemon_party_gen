#!/bin/sh
set -eu

mkdir -p "${CODEX_HOME:-/codex-home}"

cp /codex-default/config.toml "${CODEX_HOME:-/codex-home}/config.toml"

exec "$@"
