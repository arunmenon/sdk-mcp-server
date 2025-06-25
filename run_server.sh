#!/bin/bash
# Activate virtual environment and run the MCP server
cd "$(dirname "$0")"
source venv/bin/activate
exec python src/server.py