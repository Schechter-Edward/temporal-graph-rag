#!/usr/bin/env bash
set -euo pipefail

INPUT=${1:-assets/architecture.mmd}
OUTPUT=${2:-assets/architecture.png}

# Uses Mermaid CLI via npx to avoid a global install.
# Requires Node.js to be installed.

npx -y @mermaid-js/mermaid-cli -i "$INPUT" -o "$OUTPUT" -b transparent

echo "Wrote $OUTPUT"
