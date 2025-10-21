#!/usr/bin/env bash


# Check for required environment variables
if [ -z "$DATAROBOT_API_TOKEN" ]; then
    echo "Error: DATAROBOT_API_TOKEN environment variable is required"
    exit 1
fi

if [ -z "$DATAROBOT_ENDPOINT" ]; then
    echo "Error: DATAROBOT_ENDPOINT environment variable is required"
    exit 1
fi

# Start the MCP server
echo "Starting MCP server..."
# Remove this as soon as the dr-mcp-server-lib is installed via package manager
export PYTHONPATH="/opt/code/.internal/dr-mcp-server-lib:${PYTHONPATH}"
python -m app.main
