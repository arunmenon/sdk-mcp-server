#!/bin/bash

# Run the dynamic SDK-agnostic MCP server

echo "Starting Multi-SDK MCP Server..."
echo "================================"

# Change to script directory
cd "$(dirname "$0")"

# Run the dynamic server
python src/server_dynamic.py