#!/bin/sh
echo "MISO Watchdog Service: Initializing..."
while true; do
  if ! docker info > /dev/null 2>&1; then
    echo "[CRITICAL] Docker daemon is unresponsive."
  else
    echo "[INFO] Docker daemon is healthy."
  fi
  sleep 300
done
