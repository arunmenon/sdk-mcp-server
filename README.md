# SDK MCP Server

A configurable Model Context Protocol (MCP) server that provides searchable access to multiple AI/ML SDK documentation and source code. Currently supports OpenAI Agents SDK and Google ADK, with easy extensibility for additional SDKs.

## Purpose

When working with AI/ML SDKs, you often need to:
- Understand how classes and methods work internally across different SDKs
- Compare implementations between different frameworks
- Find the right method signatures and parameters
- See real implementation examples
- Debug issues by examining SDK source code

This MCP server gives AI assistants like Claude instant access to multiple SDK sources, making it a powerful development companion for multi-SDK projects.

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download SDK sources**:
```bash
python src/download_sdk.py
```
This will download all configured SDKs from `sdks.yaml`.

3. **Configure in Claude Desktop**:

Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "sdk-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/sdk-mcp-server/src/server.py"]
    }
  }
}
```

## Available Tools

Each configured SDK gets its own set of tools with the SDK prefix. Currently configured:

### OpenAI Agents SDK Tools (prefix: `openai_agents_`)

- **`openai_agents_list_files()`** - List all available OpenAI SDK source files
- **`openai_agents_get_source(filename)`** - Get source code of specific file
- **`openai_agents_search_code(query)`** - Search for terms, methods, or patterns
- **`openai_agents_get_class(class_name)`** - Extract complete class definition
- **`openai_agents_find_examples(topic)`** - Find usage examples and patterns

### Google ADK Tools (prefix: `google_adk_`)

- **`google_adk_list_files()`** - List all available Google ADK source files
- **`google_adk_get_source(filename)`** - Get source code of specific file
- **`google_adk_search_code(query)`** - Search for terms, methods, or patterns
- **`google_adk_get_class(class_name)`** - Extract complete class definition
- **`google_adk_find_examples(topic)`** - Find usage examples and patterns

### Cross-SDK Tools (coming soon)

- **`list_available_sdks()`** - Show all configured SDKs
- **`search_all_sdks(query)`** - Search across all SDKs simultaneously
- **`compare_implementations(concept, sdk_ids)`** - Compare similar concepts across SDKs

## Usage Examples

### Comparing SDKs:
```
You: "How do OpenAI and Google handle agent creation differently?"
Claude: [Uses openai_agents_get_class("Agent") and google_adk_get_class("Agent")]
*Compares the different approaches and APIs*
```

### Learning a new SDK:
```
You: "Show me how to use tools in Google ADK"
Claude: [Uses google_adk_search_code("tool") and google_adk_find_examples("tool")]
*Explains Google's approach with real examples*
```

### Debugging across SDKs:
```
You: "Why does handoff work in OpenAI but not in my Google ADK code?"
Claude: [Searches both SDKs for handoff implementations]
*Identifies the differences and helps fix the issue*
```

## Configuration

### Adding a New SDK

Edit `sdks.yaml` to add new SDKs:

```yaml
sdks:
  your_sdk:
    name: "Your SDK Name"
    description: "Description of the SDK"
    source:
      type: "github"
      repo: "org/repo-name"
      branch: "main"
      path: "src"
    file_patterns:
      - "**/*.py"
    tools:
      prefix: "your_sdk"
      descriptions:
        list_files: "List all Your SDK source files"
        # ... other tool descriptions
```

### Supported Source Types

- **GitHub repositories** - Public repos with Python/TypeScript code
- **Direct URLs** (coming soon) - ZIP/TAR archives
- **Local paths** (coming soon) - Local SDK installations

## File Structure

```
sdk-mcp-server/
├── src/
│   ├── server.py           # Main MCP server implementation
│   └── download_sdk.py     # SDK downloader and indexer
├── data/                   # Downloaded SDK files (git-ignored)
│   ├── openai_agents/      # OpenAI SDK files
│   └── google_adk/         # Google ADK files
├── sdks.yaml              # SDK configuration
├── requirements.txt       # Python dependencies
└── run_server.sh         # Server startup script
```

## Updating

To get the latest SDK sources:
```bash
python src/download_sdk.py
```

This fetches the latest code from all configured SDKs in `sdks.yaml`.

## Tips for Best Results

1. **Specify the SDK** - Mention which SDK you're working with
2. **Use SDK prefixes** - Each tool is prefixed with the SDK name
3. **Compare implementations** - Ask about differences between SDKs
4. **Request examples** - Each SDK has example-finding capabilities

## Why This Helps

- **Multi-SDK support** - Work with multiple frameworks seamlessly
- **Instant answers** - No need to browse multiple repos or docs
- **Direct comparisons** - See how different SDKs solve similar problems
- **Accurate information** - Always from the latest source code
- **Context-aware** - AI understands full implementations across SDKs

## Contributing

To add support for a new SDK:

1. Add configuration to `sdks.yaml`
2. Test with `python src/download_sdk.py`
3. Submit a pull request

## License

MIT License - see LICENSE file for details.