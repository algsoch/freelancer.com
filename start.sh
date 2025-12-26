#!/bin/bash

# AI Bid Writer - Start Script

echo "🚀 Starting AI Bid Writer..."
echo ""

# Start backend
echo "Starting backend server..."
cd "$(dirname "$0")"
source venv/bin/activate
cd backend
python main.py &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start frontend
echo ""
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"

echo ""
echo "🎉 AI Bid Writer is running!"
echo ""
echo "📝 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
