# Installation Guide for OpenAI Agents SDK MCP Server

## Prerequisites
- Python 3.8+
- Claude Desktop app

## Installation Steps

### 1. Clone or Download this Repository
```bash
cd /Users/arunmenon/projects/DeepResearcher/
# If you move it elsewhere, update paths accordingly
```

### 2. Set up Virtual Environment
```bash
cd openai-agents-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Download SDK Source Code
```bash
python src/download_sdk.py
```
This downloads all OpenAI Agents SDK source files to the `data/` directory.

### 4. Configure Claude Desktop

Add this to your Claude Desktop configuration:

**Option A: Direct Python Path (if you have Python in PATH)**
```json
{
  "mcpServers": {
    "openai-agents-sdk": {
      "command": "python",
      "args": ["/Users/arunmenon/projects/DeepResearcher/openai-agents-mcp/src/server.py"],
      "env": {
        "PYTHONPATH": "/Users/arunmenon/projects/DeepResearcher/openai-agents-mcp"
      }
    }
  }
}
```

**Option B: Using the Shell Script (Recommended)**
```json
{
  "mcpServers": {
    "openai-agents-sdk": {
      "command": "/Users/arunmenon/projects/DeepResearcher/openai-agents-mcp/run_server.sh"
    }
  }
}
```

### 5. Restart Claude Desktop

After adding the configuration, restart Claude Desktop for the changes to take effect.

## Verifying Installation

Once configured, you can test by asking Claude:
- "List OpenAI Agents SDK files"
- "Show me the Agent class from OpenAI SDK"
- "Search for handoff in the OpenAI SDK"

## Troubleshooting

### Server won't start
1. Check Python version: `python --version` (should be 3.8+)
2. Verify virtual environment is activated
3. Check all dependencies installed: `pip list`

### Tools not appearing in Claude
1. Ensure the path in config is absolute (not relative)
2. Check Claude Desktop logs for errors
3. Try running the server manually: `./run_server.sh`

### Permission errors
```bash
chmod +x run_server.sh
```

## Updating SDK Source

To get the latest SDK code:
```bash
source venv/bin/activate
python src/download_sdk.py
```