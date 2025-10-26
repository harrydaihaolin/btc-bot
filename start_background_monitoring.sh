#!/bin/bash

# BTC Tennis Bot - Background Monitoring Startup Script
# This script starts the bot in background monitoring mode as a detached process

echo "🎾 BTC Tennis Bot - Starting Background Monitoring"
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if the bot script exists
if [ ! -f "btc_tennis_bot.py" ]; then
    echo "❌ btc_tennis_bot.py not found in current directory"
    exit 1
fi

# Check if the background monitoring script exists
if [ ! -f "run_background_monitoring.py" ]; then
    echo "❌ run_background_monitoring.py not found in current directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for this session
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/btc_background_${TIMESTAMP}.log"
PID_FILE="btc_background_${TIMESTAMP}.pid"

echo "📝 Log file: $LOG_FILE"
echo "🆔 PID file: $PID_FILE"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping background monitoring..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Sending SIGTERM to process $PID..."
            kill -TERM "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                echo "Force killing process $PID..."
                kill -KILL "$PID"
            fi
        fi
        rm -f "$PID_FILE"
    fi
    echo "✅ Background monitoring stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the background monitoring process
echo "🚀 Starting background monitoring process..."
echo "   Monitoring interval: 5 minutes (configurable)"
echo "   Max attempts: Unlimited"
echo "   Headless mode: Enabled"
echo ""

# Run the background monitoring script
nohup python3 run_background_monitoring.py > "$LOG_FILE" 2>&1 &
BG_PID=$!

# Save PID to file
echo $BG_PID > "$PID_FILE"

echo "✅ Background monitoring started!"
echo "   Process ID: $BG_PID"
echo "   Log file: $LOG_FILE"
echo "   PID file: $PID_FILE"
echo ""
echo "📋 Monitoring Commands:"
echo "   View logs: tail -f $LOG_FILE"
echo "   Check status: ps -p $BG_PID"
echo "   Stop monitoring: kill $BG_PID"
echo "   Or press Ctrl+C to stop this script"
echo ""

# Wait for the background process
wait $BG_PID

# Cleanup
cleanup
