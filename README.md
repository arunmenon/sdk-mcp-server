# OpenAI Agents SDK MCP Server

A Model Context Protocol (MCP) server that provides direct access to OpenAI Agents Python SDK source code for Claude Code and other AI assistants.

## Purpose

When working with OpenAI's Agents SDK, you often need to:
- Understand how classes like `Agent`, `Tool`, and `Handoff` work internally
- Find the right method signatures and parameters
- See real implementation examples
- Debug issues by examining SDK source code

This MCP server gives Claude Code instant access to the entire SDK source, making it a powerful development companion.

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download SDK source**:
```bash
python src/download_sdk.py
```

3. **Configure in Claude Desktop**:

Add to your settings:
```json
{
  "mcpServers": {
    "openai-agents-sdk": {
      "command": "python",
      "args": ["/absolute/path/to/openai-agents-mcp/src/server.py"]
    }
  }
}
```

## Available Tools

### 🔍 `openai_agents_search_code`
Search the entire SDK for specific terms, methods, or patterns.

**Example uses**:
- "How does handoff work?" → Search for "handoff"
- "Find streaming examples" → Search for "stream"
- "Where is Tool.register defined?" → Search for "def register"

### 📄 `openai_agents_get_source`
Read the complete source code of any SDK file.

**Example uses**:
- Get Agent class: `openai_agents_get_source("agents_agent.md")`
- Get Tool implementation: `openai_agents_get_source("agents_tool.md")`

### 🏛️ `openai_agents_get_class`
Extract a complete class definition with all its methods.

**Example uses**:
- "Show me the Agent class" → `openai_agents_get_class("Agent")`
- "How is Tool implemented?" → `openai_agents_get_class("Tool")`

### 📁 `openai_agents_list_files`
Browse all available SDK source files.

**Example uses**:
- "What files are in the SDK?"
- "Show me all model provider files"

### 💡 `openai_agents_find_examples`
Find usage examples and patterns for specific features.

**Example uses**:
- "Show tool examples" → `openai_agents_find_examples("tool")`
- "Find handoff patterns" → `openai_agents_find_examples("handoff")`

## Usage Examples

### When building an agent:
```
You: "How do I create an agent with tools in OpenAI SDK?"
Claude: [Uses openai_agents_get_class("Agent") and openai_agents_find_examples("tool")]
*Shows you the Agent class constructor and tool registration examples*
```

### When debugging:
```
You: "Why is my handoff not working?"
Claude: [Uses openai_agents_search_code("handoff") and openai_agents_get_source("agents_handoffs.md")]
*Examines the handoff implementation to help debug*
```

### When learning:
```
You: "Explain how the OpenAI SDK handles streaming"
Claude: [Uses openai_agents_search_code("stream") and finds relevant implementations]
*Explains based on actual SDK code*
```

## File Structure

All SDK files are stored flat in the `data/` directory:
- `agents_agent.md` - Core Agent class
- `agents_tool.md` - Tool system
- `agents_handoffs.md` - Handoff functionality
- `agents_models_*.md` - Model providers
- `agents_voice_*.md` - Voice capabilities
- And 70+ more files...

## Updating

To get the latest SDK source:
```bash
python src/download_sdk.py
```

This fetches the latest code from the `openai/openai-agents-python` repository.

## Tips for Best Results

1. **Be specific** when asking about SDK features
2. **Mention "OpenAI Agents SDK"** or "OpenAI SDK" in your questions
3. **Reference specific classes** like Agent, Tool, Handoff
4. **Ask for examples** when learning new features

## Why This Helps

- **Instant answers** - No need to browse GitHub or docs
- **Accurate information** - Direct from source code
- **Context-aware** - Claude understands the full implementation
- **Debugging aid** - See exactly how things work internally