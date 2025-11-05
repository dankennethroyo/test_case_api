!/usr/bin/env sh
# Generate a .env file for WSL2 NAT mode with the correct Windows host IP.
# Usage: ./generate-env.sh [path-to-.env]
# Default output is ./ .env

set -eu

OUTFILE="${1:-.env}"

# 1) Discover the Windows host (gateway) IP as seen from WSL (NAT mode)
#    This is the Microsoft-documented way to reach Windows from WSL in NAT mode.
#    (Do not quote this heredoc if you want variable expansion later.)
WIN_HOST="$(ip route show | awk '/default/ {print $3}' || true)"

if [ -z "${WIN_HOST}" ]; then
  echo "ERROR: Could not determine Windows host IP from 'ip route'. Are you inside WSL?" >&2
  exit 1
fi

# 2) Backup existing .env if present
if [ -f "$OUTFILE" ]; then
  ts="$(date +%Y%m%d-%H%M%S)"
  cp -f "$OUTFILE" "${OUTFILE}.bak-${ts}"
  echo "Backed up existing ${OUTFILE} -> ${OUTFILE}.bak-${ts}"
fi

# 3) Write the new .env (unquoted heredoc to allow $WIN_HOST expansion)
cat > "$OUTFILE" <<EOF
# Test Case Generator API Configuration

# Ollama Configuration
OLLAMA_BASE_URL=http://${WIN_HOST}:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=180

# Flask Configuration
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=False
DEBUG_MODE=False

# Environment Type (development or production)
ENVIRONMENT=production

# File Upload Configuration
MAX_FILE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
EOF

echo "Wrote ${OUTFILE} with OLLAMA_BASE_URL=http://${WIN_HOST}:11434"

# 4) Optional quick connectivity check to Ollama (will succeed if Windows Ollama is running and listening)
if command -v curl >/dev/null 2>&1; then
  echo "Testing connectivity to Ollama at http://${WIN_HOST}:11434/api/tags ..."
  if curl -fsS --max-time 2 "http://${WIN_HOST}:11434/api/tags" >/dev/null; then
    echo "✅ Ollama API reachable from WSL."
  else
    echo "⚠️  Could not reach Ollama API. If you're in NAT mode, make sure on Windows:"
    echo "    - Set user env var: OLLAMA_HOST=0.0.0.0:11434"
    echo "    - Restart the Ollama app/service"
    echo "    - Allow TCP 11434 on Private network in Windows Firewall"
  fi
fi
