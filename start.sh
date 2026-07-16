#!/bin/bash
# starts both real services in one container - fastapi backend, then
# streamlit frontend, talking to each other over real http on localhost.
# this exists because HF Spaces (free tier) only runs one container per
# space. the two services are otherwise completely unchanged - still fully
# separate processes, still communicating over a real network call, just
# sharing one container instead of docker-compose's two.

set -e

echo "starting fastapi backend..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

echo "waiting for backend to be ready..."
until python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null; do
    sleep 1
done
echo "backend is ready"

echo "starting streamlit frontend on the port HF Spaces expects..."
export CLAUSEGUARD_API_URL="http://localhost:8000/analyze"
streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 7860 --server.headless true
