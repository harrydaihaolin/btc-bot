#!/bin/bash
# Start BTC Tennis Bot Daemon Monitoring

echo "🚀 Starting BTC Tennis Bot Daemon Monitoring..."
echo "   Monitoring interval: 5 minutes"
echo "   Max scans: Unlimited (0)"
echo "   Log file: btc_daemon.log"
echo ""

# Start daemon with pre-configured settings
echo -e "5\n0" | python3 daemon_monitoring.py > btc_daemon.log 2>&1 &

# Get the PID
DAEMON_PID=$!

# Save PID to file
echo $DAEMON_PID > btc_daemon.pid

echo "✅ Daemon started with PID: $DAEMON_PID"
echo "📝 Logs are being written to: btc_daemon.log"
echo "🛑 To stop: kill $DAEMON_PID or run: ./stop_daemon.sh"
echo ""
echo "📊 Monitor status with: tail -f btc_daemon.log"
