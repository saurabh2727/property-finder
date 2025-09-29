#!/bin/bash

# Kill Property Finder Streamlit Server
# This script will find and kill any running Streamlit processes

echo "🔍 Searching for running Streamlit processes..."

# Find Streamlit processes
STREAMLIT_PIDS=$(ps aux | grep -E "streamlit.*app\.py|streamlit.*run" | grep -v grep | awk '{print $2}')

if [ -z "$STREAMLIT_PIDS" ]; then
    echo "ℹ️  No Streamlit processes found running"
else
    echo "🎯 Found Streamlit processes with PIDs: $STREAMLIT_PIDS"

    # Kill each process
    for PID in $STREAMLIT_PIDS; do
        echo "🔪 Killing process $PID..."
        kill -9 $PID
        if [ $? -eq 0 ]; then
            echo "✅ Successfully killed process $PID"
        else
            echo "❌ Failed to kill process $PID"
        fi
    done
fi

# Also check for any processes using port 8501 (default Streamlit port)
echo ""
echo "🔍 Checking for processes using port 8501..."

PORT_PIDS=$(lsof -ti:8501)

if [ -z "$PORT_PIDS" ]; then
    echo "ℹ️  No processes found using port 8501"
else
    echo "🎯 Found processes using port 8501 with PIDs: $PORT_PIDS"

    for PID in $PORT_PIDS; do
        echo "🔪 Killing process $PID on port 8501..."
        kill -9 $PID
        if [ $? -eq 0 ]; then
            echo "✅ Successfully killed process $PID"
        else
            echo "❌ Failed to kill process $PID"
        fi
    done
fi

# Check for any other common Streamlit ports
for PORT in 8502 8503 8504; do
    PORT_PIDS=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$PORT_PIDS" ]; then
        echo "🎯 Found processes using port $PORT with PIDs: $PORT_PIDS"
        for PID in $PORT_PIDS; do
            echo "🔪 Killing process $PID on port $PORT..."
            kill -9 $PID
        done
    fi
done

echo ""
echo "🎉 Server cleanup complete!"
echo "💡 You can now run './run_app.sh' to start a fresh server"