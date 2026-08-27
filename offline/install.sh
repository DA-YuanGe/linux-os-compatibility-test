#!/bin/sh

set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OFFLINE_DIR="$PROJECT_ROOT/offline"

PACKAGES_DIR="$OFFLINE_DIR/packages"
CONFIG_DIR="$OFFLINE_DIR/config"
RUNTIME_DIR="$OFFLINE_DIR/runtime"
LOG_DIR="$OFFLINE_DIR/logs"

MODE="online"

if [ "${1:-}" = "--offline" ]; then
    MODE="offline"
fi

echo "========================================"
echo " Linux Application Deployment"
echo "========================================"
echo "Mode: $MODE"
echo "Project: $PROJECT_ROOT"
echo

echo "[1/6] Checking offline package directory..."

if [ ! -d "$PACKAGES_DIR" ]; then
    echo "FAIL: Offline package directory not found."
    exit 1
fi

if [ ! -f "$PACKAGES_DIR/demo-app.sh" ]; then
    echo "FAIL: Required offline package not found."
    exit 1
fi

echo "PASS: Offline package found."
echo

echo "[2/6] Checking configuration..."

if [ ! -f "$CONFIG_DIR/demo-app.conf" ]; then
    echo "FAIL: Application configuration not found."
    exit 1
fi

echo "PASS: Configuration found."
echo

echo "[3/6] Checking required runtime..."

if ! command -v sh >/dev/null 2>&1; then
    echo "FAIL: Required shell runtime is unavailable."
    exit 1
fi

echo "PASS: Shell runtime available."
echo

echo "[4/6] Preparing runtime directories..."

mkdir -p "$RUNTIME_DIR"
mkdir -p "$LOG_DIR"

echo "PASS: Runtime directories prepared."
echo

echo "[5/6] Installing application from local package..."

cp "$PACKAGES_DIR/demo-app.sh" \
   "$RUNTIME_DIR/demo-app.sh"

chmod +x "$RUNTIME_DIR/demo-app.sh"

cp "$CONFIG_DIR/demo-app.conf" \
   "$RUNTIME_DIR/demo-app.conf"

echo "PASS: Application installed from offline package."
echo

echo "[6/6] Running offline deployment verification..."

OUTPUT="$("$RUNTIME_DIR/demo-app.sh")"

if [ "$OUTPUT" != "offline-demo-app-installed" ]; then
    echo "FAIL: Application verification failed."
    exit 1
fi

printf '%s\n' "$OUTPUT" > "$LOG_DIR/demo-app.log"

echo "PASS: Application executed successfully."
echo

echo "========================================"
echo " Offline Deployment Result: PASS"
echo "========================================"
echo "Runtime: $RUNTIME_DIR"
echo "Config : $RUNTIME_DIR/demo-app.conf"
echo "Log    : $LOG_DIR/demo-app.log"
