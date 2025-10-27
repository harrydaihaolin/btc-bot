#!/bin/bash
# Simple BTC Tennis Bot Daemon Runner
# One-command daemon startup with configurable intervals

echo "🎾 BTC Tennis Bot - Simple Daemon Mode"
echo "======================================"

# Default monitoring interval (in minutes)
INTERVAL=${1:-60}

echo "Monitoring interval: $INTERVAL minutes"
echo ""

# Set monitoring interval environment variable
export BTC_MONITORING_INTERVAL=$INTERVAL

# Set non-interactive mode for daemon
export FORCE_INTERACTIVE=false

# Start daemon with proper logging
echo "🚀 Starting daemon monitoring..."
nohup python3 btc_bot.py > btc_daemon.log 2>&1 &

# Get PID
DAEMON_PID=$!

# Save PID
echo $DAEMON_PID > btc_daemon.pid

echo "✅ Daemon started successfully!"
echo "   PID: $DAEMON_PID"
echo "   Log: btc_daemon.log"
echo "   Interval: $INTERVAL minutes"
echo ""
echo "📊 Monitor with: tail -f btc_daemon.log"
echo "🛑 Stop with: kill $DAEMON_PID"
echo ""
echo "🎾 Bot is now monitoring for tennis courts every $INTERVAL minutes!"
