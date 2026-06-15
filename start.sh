#!/bin/sh
# Start OpenTelemetry Collector in the background if ENABLE_TELEMETRY is True
if [ "$ENABLE_TELEMETRY" = "True" ] || [ "$ENABLE_TELEMETRY" = "true" ]; then
    echo "Starting OpenTelemetry Collector..."
    otelcol-contrib --config otel-collector-config.yaml > otelcol.log 2>&1 &
fi

echo "Starting FastAPI Application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
