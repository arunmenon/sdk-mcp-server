#!/usr/bin/env python3
"""
Simple MCP Server for OpenAI Agents SDK Reference
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional

from fastmcp import FastMCP

# Initialize server
mcp = FastMCP("OpenAI Agents SDK")

# Get data directory
DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_FILE = DATA_DIR / "index.json"

# Load index
def load_index():
    """Load the file index."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r') as f:
            return json.load(f)
    return {"files": []}

# --- Tools ---

@mcp.tool()
def openai_agents_list_files() -> List[str]:
    """
    List all OpenAI Agents SDK source files available for browsing.
    
    Use this to explore the SDK structure and find specific modules like:
    - agents_agent.md (main Agent class)
    - agents_tool.md (Tool registration and execution)
    - agents_handoffs.md (Handoff system)
    - agents_models_*.md (Model provider implementations)
    
    Returns:
        List of available SDK source file names
    """
    index = load_index()
    return [f["saved_as"] for f in index.get("files", [])]


@mcp.tool()
def openai_agents_get_source(filename: str) -> str:
    """
    Read the source code of a specific OpenAI Agents SDK file.
    
    Use this to examine implementation details, class definitions, method signatures,
    and understand how OpenAI Agents SDK components work internally.
    
    Args:
        filename: SDK file name (e.g., "agents_agent.md" for Agent class source)
        
    Returns:
        Complete source code of the requested file
    
    Example:
        openai_agents_get_source("agents_tool.md") - Get Tool class implementation
        openai_agents_get_source("agents_handoffs.md") - Get Handoff system code
    """
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return f"File not found: {filename}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


@mcp.tool()
def openai_agents_search_code(query: str, case_sensitive: bool = False) -> Dict[str, List[str]]:
    """
    Search OpenAI Agents SDK source code for specific terms, methods, or patterns.
    
    Perfect for finding:
    - Method implementations (e.g., "def run", "def register")
    - Class usages (e.g., "class Agent", "extends Tool")
    - Import statements (e.g., "from agents import")
    - Specific functionality (e.g., "handoff", "streaming", "voice")
    
    Args:
        query: Search term (method name, class, keyword, etc.)
        case_sensitive: Whether to match case exactly (default: False)
        
    Returns:
        Dictionary mapping filenames to matching code lines (max 10 per file)
    """
    results = {}
    
    # Convert query for case-insensitive search
    if not case_sensitive:
        query = query.lower()
    
    # Search all markdown files
    for md_file in DATA_DIR.glob("*.md"):
        matches = []
        
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            search_line = line if case_sensitive else line.lower()
            if query in search_line:
                matches.append(f"Line {i}: {line.strip()}")
        
        if matches:
            results[md_file.name] = matches[:10]  # Limit to 10 matches per file
    
    return results


@mcp.tool()
def openai_agents_get_class(class_name: str) -> Optional[str]:
    """
    Extract complete class definition from OpenAI Agents SDK.
    
    Retrieves the full class implementation including:
    - Class signature and inheritance
    - Docstring and documentation
    - Method definitions
    - Properties and attributes
    
    Common classes to explore:
    - Agent: Main agent class for creating AI agents
    - Tool: Base class for tool implementations
    - Handoff: Managing agent-to-agent handoffs
    - Runner: Execution and orchestration
    - Model: LLM provider interfaces
    
    Args:
        class_name: Name of the class (e.g., "Agent", "Tool", "Handoff")
        
    Returns:
        Complete class definition with methods and docstrings
        
    Example:
        openai_agents_get_class("Agent") - Get the Agent class implementation
        openai_agents_get_class("Tool") - Understand how tools are defined
    """
    # Search for class definition
    search_results = openai_agents_search_code(f"class {class_name}", case_sensitive=True)
    
    if not search_results:
        return f"Class '{class_name}' not found"
    
    # Get the first file with the class
    for filename, matches in search_results.items():
        content = openai_agents_get_source(filename)
        
        # Extract class definition and following lines
        lines = content.split('\n')
        class_info = []
        in_class = False
        indent_level = 0
        
        for line in lines:
            if f"class {class_name}" in line:
                in_class = True
                indent_level = len(line) - len(line.lstrip())
                class_info.append(line)
            elif in_class:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level:
                    break
                class_info.append(line)
        
        if class_info:
            return '\n'.join(class_info[:50])  # Return first 50 lines
    
    return f"Class '{class_name}' definition not found"


@mcp.tool()
def openai_agents_find_examples(topic: str) -> Dict[str, List[str]]:
    """
    Find code examples and usage patterns in OpenAI Agents SDK.
    
    Searches for practical examples of how to use specific features:
    - Tool registration examples
    - Agent initialization patterns
    - Handoff implementations
    - Streaming setups
    - Error handling patterns
    
    Args:
        topic: Feature or pattern to find examples for (e.g., "tool", "handoff", "stream")
        
    Returns:
        Dictionary of files containing relevant examples with code snippets
        
    Example:
        openai_agents_find_examples("tool") - Find tool implementation examples
        openai_agents_find_examples("handoff") - Find handoff usage patterns
    """
    # Search for examples related to the topic
    results = openai_agents_search_code(topic, case_sensitive=False)
    
    # Filter and enhance results to show more context
    examples = {}
    for filename, matches in results.items():
        # Look for method definitions, class usage, etc.
        enhanced_matches = []
        for match in matches:
            # Include matches that look like examples
            if any(keyword in match.lower() for keyword in ['def ', 'class ', '= ', 'self.', topic.lower()]):
                enhanced_matches.append(match)
        
        if enhanced_matches:
            examples[filename] = enhanced_matches[:5]  # Top 5 examples per file
    
    return examples


# --- Main ---

if __name__ == "__main__":
    print("OpenAI Agents SDK MCP Server")
    print(f"Data directory: {DATA_DIR}")
    print(f"Files available: {len(list(DATA_DIR.glob('*.md')))}")
    mcp.run()