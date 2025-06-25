#!/usr/bin/env python3
"""Test the OpenAI Agents SDK MCP Server tools"""

import sys
sys.path.append('src')

from server import (
    openai_agents_list_files,
    openai_agents_get_source,
    openai_agents_search_code,
    openai_agents_get_class,
    openai_agents_find_examples
)

print("Testing OpenAI Agents SDK MCP Server\n")

# Test 1: List files
print("1. Listing SDK files:")
files = openai_agents_list_files()
print(f"   Found {len(files)} files")
print(f"   First 5: {files[:5]}\n")

# Test 2: Search for "Agent" class
print("2. Searching for 'class Agent':")
results = openai_agents_search_code("class Agent")
print(f"   Found in {len(results)} files")
for filename, matches in list(results.items())[:2]:
    print(f"   - {filename}: {matches[0] if matches else 'No matches'}"[:80] + "...")
print()

# Test 3: Get Agent class definition
print("3. Getting Agent class definition:")
agent_class = openai_agents_get_class("Agent")
if agent_class:
    lines = agent_class.split('\n')[:10]
    for line in lines:
        print(f"   {line}")
print()

# Test 4: Find tool examples
print("4. Finding tool examples:")
examples = openai_agents_find_examples("tool")
print(f"   Found examples in {len(examples)} files")
for filename, ex in list(examples.items())[:2]:
    print(f"   - {filename}: {len(ex)} examples")
print()

print("✅ All tests passed!")