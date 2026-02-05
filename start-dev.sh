#!/bin/bash
# start-dev.sh - Start all services for local development
# Usage: ./start-dev.sh

set -e

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export APP_ENV=development

echo ""
echo "Starting Company Tracker (development mode)"
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:8501"
echo "  Database: SQLite (company_tracker.db)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Track background PIDs for cleanup
cleanup() {
    echo ""
    echo "Stopping services..."
    # Send SIGTERM individually to avoid reentrant signal issues
    kill -TERM $API_PID 2>/dev/null
    kill -TERM $FRONTEND_PID 2>/dev/null
    wait $API_PID $FRONTEND_PID 2>/dev/null
    echo "All services stopped."
    exit 0
}

# Ignore SIGINT in the parent so it doesn't propagate to children via
# the process group. We handle shutdown ourselves via the trap.
trap cleanup SIGINT SIGTERM

# Start processes in their own process groups (setsid) so Ctrl+C
# doesn't hit them directly — we send SIGTERM in cleanup instead.
setsid uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!

setsid streamlit run frontend/Home.py --server.address 127.0.0.1 --server.port 8501 &
FRONTEND_PID=$!

# Wait for either to exit
wait -n $API_PID $FRONTEND_PID
cleanup
