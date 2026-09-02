#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="scorer"
SCORE_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_USER="${SUDO_USER:-$(whoami)}"
PYTHON_BIN="$(command -v python3)"

UNIT_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root (use sudo)." >&2
    exit 1
fi

cat > "$UNIT_FILE" <<EOF
[Unit]
Description=Resume Scorer Web UI
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${SCORE_DIR}
ExecStart=${PYTHON_BIN} ./app.py
Restart=on-failure
RestartSec=5
Environment=PORT=8080

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "Service '${SERVICE_NAME}' installed and started."
echo "  Status : systemctl status ${SERVICE_NAME}"
echo "  Logs   : journalctl -u ${SERVICE_NAME} -f"
echo "  Stop   : sudo systemctl stop ${SERVICE_NAME}"
