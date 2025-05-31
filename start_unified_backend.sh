#!/bin/bash

# Unified Backend System Startup Script

echo "🚀 Starting Unified Romanian Admin Platform..."

# Start Unified FastAPI Backend with Auto-Archive
echo "📡 Starting unified FastAPI backend..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start Frontend Development Server
echo "🌐 Starting React frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ System started successfully!"
echo "🔗 Unified Backend API: http://localhost:8000"
echo "🔗 API Documentation: http://localhost:8000/api/docs"
echo "🔗 Frontend App: http://localhost:3000"
echo ""
echo "📋 Available endpoints:"
echo "  - Authentication: /api/auth/*"
echo "  - Users: /api/users/*"
echo "  - Documents: /api/documents/*"
echo "  - Archive: /api/archive/*"
echo "  - Auto-Archive Upload: /api/auto-archive/upload-pdf"
echo "  - Auto-Archive Scan: /api/auto-archive/scan-and-archive"
echo "  - OCR Processing: /api/auto-archive/upload-and-process"
echo "  - Document Search: /api/auto-archive/search"
echo ""
echo "⚠️  Prerequisites:"
echo "  - GEMINI_API_KEY set in backend/.env"
echo "  - NAPS2 installed (for scanning functionality)"
echo "  - PostgreSQL database running"
echo ""
echo "🛑 To stop the system, press Ctrl+C"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping Unified Backend System..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ System stopped."
    exit 0
}

# Handle Ctrl+C
trap cleanup SIGINT

# Wait for user to press Ctrl+C
wait 