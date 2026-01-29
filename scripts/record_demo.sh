#!/usr/bin/env bash
set -euo pipefail

OUTPUT_CAST=${1:-assets/demo.cast}
OUTPUT_GIF=${2:-assets/demo.gif}

AGG_BIN=${AGG_BIN:-$HOME/.cargo/bin/agg}

# Requires: asciinema and agg (asciinema-agg)
# Example:
#   sudo apt install asciinema
#   cargo install --locked asciinema-agg

asciinema rec -c "python demo/cli_demo.py 'Who managed infrastructure before the March 2024 reorg?' --reference-time 2024-06-01T00:00:00" "$OUTPUT_CAST"

if [ ! -x "$AGG_BIN" ]; then
  echo "agg not found at $AGG_BIN"
  echo "Set AGG_BIN or install agg: cargo install --git https://github.com/asciinema/agg --locked"
  exit 1
fi

"$AGG_BIN" "$OUTPUT_CAST" "$OUTPUT_GIF"

echo "Wrote $OUTPUT_GIF"
