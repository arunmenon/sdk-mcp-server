#!/usr/bin/env python3
"""
Dynamic MCP Server - SDK-agnostic implementation
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

from src.registry import SDKRegistry
from src.providers import ProviderFactory
from src.indexer import SDKIndexer
from src.search import SDKSearchEngine


class DynamicMCPServer:
    """Main MCP server supporting multiple SDKs"""
    
    def __init__(self, config_file: str = "sdks.yaml"):
        self.config_file = config_file
        self.data_dir = Path("data")
        self.cache_dir = Path("sdk_cache")
        self.index_dir = Path("indices")
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.index_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.registry = SDKRegistry(config_file)
        self.indexer = SDKIndexer()
        self.search_engine = SDKSearchEngine(self.indexer)
        self.mcp = FastMCP("Multi-SDK Documentation Server")
        
        # Load existing indices
        self.indexer.load_indices(self.index_dir)
        
        # Register all tools
        self._register_all_tools()
        self._register_meta_tools()
    
    async def initialize_sdks(self):
        """Download and index all configured SDKs"""
        for sdk_id in self.registry.list_sdks():
            try:
                await self._initialize_single_sdk(sdk_id)
            except Exception as e:
                print(f"Error initializing {sdk_id}: {e}")
    
    async def _initialize_single_sdk(self, sdk_id: str):
        """Initialize a single SDK"""
        sdk_config = self.registry.get_sdk(sdk_id)
        if not sdk_config:
            print(f"No configuration found for {sdk_id}")
            return
        
        if not self.registry.validate_sdk_config(sdk_id):
            print(f"Invalid configuration for {sdk_id}")
            return
        
        print(f"Initializing {sdk_config['name']}...")
        
        # Download SDK
        source_config = sdk_config["source"]
        source_type = source_config["type"]
        
        provider = ProviderFactory.create_provider(source_type)
        source_path = await provider.download(source_config, self.cache_dir)
        
        print(f"Downloaded {sdk_id} to {source_path}")
        
        # Index SDK
        index = await self.indexer.index_sdk(sdk_id, source_path, sdk_config)
        
        # Save source files to data directory
        await self._save_sdk_files(sdk_id, source_path, index)
        
        # Save index
        self.indexer.save_indices(self.index_dir)
        
        print(f"Indexed {len(index['files'])} files for {sdk_id}")
    
    async def _save_sdk_files(self, sdk_id: str, source_path: Path, index: Dict[str, Any]):
        """Save SDK files to data directory"""
        sdk_data_dir = self.data_dir / sdk_id
        sdk_data_dir.mkdir(exist_ok=True)
        
        for file_info in index["files"]:
            original_path = Path(file_info["original_path"])
            saved_name = file_info["saved_as"]
            
            if original_path.exists():
                # Read content
                content = original_path.read_text(encoding='utf-8', errors='ignore')
                
                # Format as markdown with source info
                formatted_content = f"# {file_info['relative_path']}\n\n```python\n{content}\n```"
                
                # Save to data directory
                output_path = sdk_data_dir / saved_name
                output_path.write_text(formatted_content, encoding='utf-8')
    
    def _register_all_tools(self):
        """Register tools for all configured SDKs"""
        for sdk_id in self.registry.list_sdks():
            sdk_config = self.registry.get_sdk(sdk_id)
            if not sdk_config:
                continue
            
            self._register_sdk_tools(sdk_id, sdk_config)
    
    def _register_sdk_tools(self, sdk_id: str, sdk_config: Dict[str, Any]):
        """Register tools for a specific SDK"""
        prefix = sdk_config.get("tools", {}).get("prefix", sdk_id)
        descriptions = sdk_config.get("tools", {}).get("descriptions", {})
        
        # Create closures to capture sdk_id
        def make_list_files_tool(sdk_id):
            def list_files() -> List[str]:
                index = self.indexer.get_index(sdk_id)
                if not index:
                    return []
                return [f["saved_as"] for f in index.get("files", [])]
            return list_files
        
        def make_get_source_tool(sdk_id):
            def get_source(filename: str) -> str:
                sdk_data_dir = self.data_dir / sdk_id
                file_path = sdk_data_dir / filename
                
                if not file_path.exists():
                    return f"File not found: {filename}"
                
                try:
                    return file_path.read_text(encoding='utf-8')
                except Exception as e:
                    return f"Error reading file: {e}"
            return get_source
        
        def make_search_code_tool(sdk_id):
            def search_code(query: str, case_sensitive: bool = False) -> Dict[str, List[str]]:
                return self.search_engine.search_code(sdk_id, query, case_sensitive=case_sensitive)
            return search_code
        
        def make_get_class_tool(sdk_id):
            def get_class(class_name: str) -> str:
                result = self.search_engine.get_class_source(sdk_id, class_name)
                return result or f"Class {class_name} not found in {sdk_id}"
            return get_class
        
        def make_find_examples_tool(sdk_id):
            def find_examples(topic: str) -> Dict[str, List[str]]:
                return self.search_engine.find_examples(sdk_id, topic)
            return find_examples
        
        # Register list_files tool
        list_tool_name = f"{prefix}_list_files"
        list_tool_desc = descriptions.get("list_files", f"List all {sdk_config['name']} source files")
        self.mcp.tool(name=list_tool_name, description=list_tool_desc)(make_list_files_tool(sdk_id))
        
        # Register get_source tool
        get_tool_name = f"{prefix}_get_source"
        get_tool_desc = descriptions.get("get_source", f"Get {sdk_config['name']} source code")
        self.mcp.tool(name=get_tool_name, description=get_tool_desc)(make_get_source_tool(sdk_id))
        
        # Register search_code tool
        search_tool_name = f"{prefix}_search_code"
        search_tool_desc = descriptions.get("search_code", f"Search {sdk_config['name']} code")
        self.mcp.tool(name=search_tool_name, description=search_tool_desc)(make_search_code_tool(sdk_id))
        
        # Register get_class tool
        class_tool_name = f"{prefix}_get_class"
        class_tool_desc = descriptions.get("get_class", f"Get {sdk_config['name']} class definition")
        self.mcp.tool(name=class_tool_name, description=class_tool_desc)(make_get_class_tool(sdk_id))
        
        # Register find_examples tool
        examples_tool_name = f"{prefix}_find_examples"
        examples_tool_desc = descriptions.get("find_examples", f"Find {sdk_config['name']} examples")
        self.mcp.tool(name=examples_tool_name, description=examples_tool_desc)(make_find_examples_tool(sdk_id))
    
    def _register_meta_tools(self):
        """Register tools that work across all SDKs"""
        
        @self.mcp.tool()
        def list_available_sdks() -> List[Dict[str, str]]:
            """List all available SDK documentation sources"""
            sdks = []
            for sdk_id in self.registry.list_sdks():
                config = self.registry.get_sdk(sdk_id)
                if config:
                    sdks.append({
                        "id": sdk_id,
                        "name": config.get("name", sdk_id),
                        "description": config.get("description", ""),
                        "tool_prefix": config.get("tools", {}).get("prefix", sdk_id)
                    })
            return sdks
        
        @self.mcp.tool()
        def search_all_sdks(query: str, case_sensitive: bool = False) -> Dict[str, Dict[str, List[str]]]:
            """Search across all available SDKs"""
            return self.search_engine.search_all_sdks(query, case_sensitive=case_sensitive)
        
        @self.mcp.tool()
        def compare_implementations(concept: str, sdk_ids: List[str]) -> Dict[str, Any]:
            """Compare how different SDKs implement similar concepts"""
            return self.search_engine.compare_implementations(concept, sdk_ids)
    
    async def run(self):
        """Run the MCP server"""
        # Initialize SDKs in the background
        asyncio.create_task(self.initialize_sdks())
        
        # Run the MCP server
        await self.mcp.run()


async def main():
    """Main entry point"""
    server = DynamicMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())