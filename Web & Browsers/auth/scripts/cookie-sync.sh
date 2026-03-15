#!/bin/bash
# Cookie Sync — Mac → Droplet
# Extracts domain-filtered cookies from local browsers,
# converts to Netscape format, pushes to droplet via Tailscale.
#
# Usage:
#   cookie-sync.sh youtube.com github.com    # sync specific domains
#   cookie-sync.sh --all                     # sync all registered domains
#
# Prerequisites:
#   - browser_cookie3 installed (pip install browser_cookie3)
#   - Python 3.12+
#   - rsync
#   - Tailscale connected to droplet
#
# Cookie store:
#   Local:  ~/.ai-cos/cookies/<domain>.txt (Netscape format, chmod 600)
#   Remote: /opt/ai-cos/cookies/<domain>.txt

set -euo pipefail

COOKIE_DIR="$HOME/.ai-cos/cookies"
LOG_FILE="$HOME/.ai-cos/logs/cookie-sync.log"
DROPLET_HOST="${DROPLET_HOST:-droplet}"  # Tailscale hostname
REMOTE_DIR="/opt/ai-cos/cookies"
PYTHON="${PYTHON:-python3}"

# Registered domains for --all mode
REGISTERED_DOMAINS=(
    ".youtube.com"
    ".google.com"
    ".github.com"
)

log() {
    local msg="$(date -u +%Y-%m-%dT%H:%M:%SZ) $1"
    echo "$msg"
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$msg" >> "$LOG_FILE"
}

extract_cookies() {
    local domain="$1"
    local output_file="$COOKIE_DIR/${domain#.}.txt"

    $PYTHON -c "
import browser_cookie3
import http.cookiejar
import sys
import os

domain = '${domain}'

# Try Safari first, then Chrome
cookies = []
for browser_fn in [browser_cookie3.safari, browser_cookie3.chrome]:
    try:
        cj = browser_fn(domain_name=domain)
        cookies.extend(cj)
    except Exception as e:
        print(f'  {browser_fn.__name__}: {e}', file=sys.stderr)

if not cookies:
    print(f'No cookies found for {domain}', file=sys.stderr)
    sys.exit(1)

# Write Netscape format
output = '${output_file}'
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w') as f:
    f.write('# Netscape HTTP Cookie File\\n')
    f.write(f'# Extracted by cookie-sync.sh for {domain}\\n')
    f.write(f'# Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)\\n')
    for c in cookies:
        secure = 'TRUE' if c.secure else 'FALSE'
        http_only = 'TRUE'  # default safe
        expiry = str(c.expires) if c.expires else '0'
        host = c.domain if c.domain.startswith('.') else '.' + c.domain
        path = c.path or '/'
        f.write(f'{host}\\tTRUE\\t{path}\\t{secure}\\t{expiry}\\t{c.name}\\t{c.value}\\n')

os.chmod(output, 0o600)
print(f'{len(cookies)} cookies extracted for {domain}')
"
}

push_to_droplet() {
    if ! command -v rsync &>/dev/null; then
        log "ERROR: rsync not found"
        return 1
    fi

    log "Pushing cookies to $DROPLET_HOST:$REMOTE_DIR"
    rsync -az --chmod=F600 "$COOKIE_DIR/" "$DROPLET_HOST:$REMOTE_DIR/" 2>&1 || {
        log "ERROR: rsync failed (is Tailscale connected?)"
        return 1
    }
    log "Push complete"
}

# --- Main ---

if [[ $# -eq 0 ]]; then
    echo "Usage: cookie-sync.sh domain1.com domain2.com"
    echo "       cookie-sync.sh --all"
    exit 1
fi

domains=()
push=true

if [[ "$1" == "--all" ]]; then
    domains=("${REGISTERED_DOMAINS[@]}")
elif [[ "$1" == "--local" ]]; then
    shift
    domains=("$@")
    push=false
else
    for d in "$@"; do
        # Ensure domain starts with dot for browser_cookie3
        [[ "$d" == .* ]] || d=".$d"
        domains+=("$d")
    done
fi

log "Starting cookie sync for ${#domains[@]} domain(s)"
mkdir -p "$COOKIE_DIR"

failed=0
for domain in "${domains[@]}"; do
    log "Extracting: $domain"
    if extract_cookies "$domain"; then
        log "  OK: $domain"
    else
        log "  FAIL: $domain"
        ((failed++))
    fi
done

if [[ "$push" == true ]]; then
    push_to_droplet
fi

if [[ $failed -gt 0 ]]; then
    log "Done with $failed failure(s)"
    exit 1
else
    log "Done — all domains synced"
fi
