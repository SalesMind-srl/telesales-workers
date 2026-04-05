#!/bin/bash
# Auto-callback service for ElevenLabs batch processing
# Only monitors callback batches from edoardo 100-200

cd "$(dirname "$0")"

export ELEVENLABS_API_KEY="3ff8fd353d2754bf2a98fa448f38e38826c1261e73984fff80b740f4d022497c"
export GHL_API_KEY="pit-ea46a302-302d-41e7-a84f-794db77a134b"
export GHL_LOCATION_ID="axueu1S0Ny1W9aeGbARf"
export ALLOWED_BATCH_PREFIX="callback: edoardo 100-200"
export CHECK_INTERVAL_MINUTES="30"

echo "Starting auto-callback service..."
echo "Monitoring: callback batches from edoardo 100-200"
echo "Check interval: ${CHECK_INTERVAL_MINUTES} min"
echo "API: http://localhost:8000"
echo "Health: http://localhost:8000/health"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
