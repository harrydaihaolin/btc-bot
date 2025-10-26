#!/bin/bash
# Stop BTC Tennis Bot Daemon Monitoring

echo "🛑 Stopping BTC Tennis Bot Daemon Monitoring..."

# Check if PID file exists
if [ -f "btc_daemon.pid" ]; then
    DAEMON_PID=$(cat btc_daemon.pid)
    
    # Check if process is still running
    if ps -p $DAEMON_PID > /dev/null 2>&1; then
        echo "   Stopping daemon with PID: $DAEMON_PID"
        kill $DAEMON_PID
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Check if it's still running
        if ps -p $DAEMON_PID > /dev/null 2>&1; then
            echo "   Force killing daemon..."
            kill -9 $DAEMON_PID
        fi
        
        echo "✅ Daemon stopped successfully"
    else
        echo "⚠️  Daemon process not found (may have already stopped)"
    fi
    
    # Remove PID file
    rm -f btc_daemon.pid
else
    echo "⚠️  No PID file found. Trying to find and stop any running daemon processes..."
    
    # Find and kill any running daemon processes
    PIDS=$(ps aux | grep daemon_monitoring | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "   Found daemon processes: $PIDS"
        kill $PIDS
        echo "✅ Daemon processes stopped"
    else
        echo "ℹ️  No daemon processes found"
    fi
fi

echo "📊 Check logs: tail btc_daemon.log"
