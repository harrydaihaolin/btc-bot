#!/bin/bash

# UBC Tennis Court Monitor - Simple Daemon Runner
# Usage: ./run_ubc_daemon.sh [monitoring_interval_minutes] [max_scans]

# Define log file and PID file paths
LOG_FILE="ubc_daemon.log"
PID_FILE="ubc_daemon.pid"

# Default values for monitoring interval and max scans
MONITORING_INTERVAL=${1:-5} # Default to 5 minutes
MAX_SCANS=${2:-0} # Default to 0 (unlimited)

# Check if daemon is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "Stopped existing UBC daemon"
        kill "$PID"
        rm -f "$PID_FILE"
        sleep 1
    fi
fi

echo "🎾 UBC Tennis Court Monitor - Simple Daemon Mode"
echo "================================================"
echo "Monitoring interval: ${MONITORING_INTERVAL} minutes"
echo ""

# Start the daemon in the background
# Use environment variables to pass configuration to the Python script
UBC_MONITORING_INTERVAL=$MONITORING_INTERVAL \
UBC_MAX_ATTEMPTS=$MAX_SCANS \
nohup python3 ubc_daemon_monitoring.py > "$LOG_FILE" 2>&1 &

# Save PID to file
echo $! > "$PID_FILE"
PID=$(cat "$PID_FILE")

echo "🚀 Starting UBC daemon monitoring..."
echo "✅ UBC daemon started successfully!"
echo "   PID: $PID"
echo "   Log: $LOG_FILE"
echo "   Interval: ${MONITORING_INTERVAL} minutes"
echo ""
echo "📊 Monitor with: tail -f $LOG_FILE"
echo "🛑 Stop with: kill $PID"
echo ""
echo "🎾 UBC Bot is now monitoring for tennis courts every ${MONITORING_INTERVAL} minutes!"
